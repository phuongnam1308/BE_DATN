from fastapi import APIRouter, HTTPException
from models import CrawlRequest, CrawlResponse, TextInput, ClassifiedInput
from crawler import crawl_facebook_page
from database import create_tables, save_raw_to_db, save_clean_to_db, save_filtered_data
from config import TRAINING_SERVICE_URL, CRAWL_DB_CONFIG, TRAINING_DB_CONFIG, SUSPICIOUS_URLS
import requests
import psycopg2
import json
import logging
import time

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def call_training_service(payload, max_attempts=3, wait_seconds=2):
    attempt = 1
    while attempt <= max_attempts:
        try:
            logger.info(f"Gửi request tới {TRAINING_SERVICE_URL}/classify-manual với payload: {payload} (Lần thử {attempt}/{max_attempts})")
            response = requests.post(
                f"{TRAINING_SERVICE_URL}/classify-manual",
                json=payload,
                timeout=20
            )
            response.raise_for_status()
            logger.info(f"Phản hồi từ Training Service: {response.json()}")
            return response.json()
        except requests.Timeout:
            logger.warning(f"Request timeout sau 20 giây (Lần thử {attempt}/{max_attempts})")
        except requests.RequestException as e:
            logger.warning(f"Lỗi khi gửi request: {str(e)} (Lần thử {attempt}/{max_attempts})")
        if attempt < max_attempts:
            time.sleep(wait_seconds)
        attempt += 1
    raise HTTPException(status_code=503, detail=f"Không thể kết nối tới Training Service sau {max_attempts} lần thử")

@router.post("/crawl", response_model=CrawlResponse)
async def crawl_endpoint(request: CrawlRequest):
    logger.info(f"Bắt đầu xử lý /crawl với url={request.url}, target_posts={request.target_posts}")
    try:
        create_tables()
        posts = crawl_facebook_page(request.url, request.target_posts)
        save_raw_to_db(posts)
        save_clean_to_db(posts, request.url)
        save_filtered_data(posts, request.url)
        return {
            "url": request.url,
            "posts": [post["text"] for post in posts],
            "message": f"Đã crawl, lưu {len(posts)} bài viết vào raw_fanpage_facebook, clean_fanpage_facebook và filtered_data!"
        }
    except Exception as e:
        logger.error(f"Lỗi khi crawl: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi khi crawl: {str(e)}")

@router.post("/manual-classify")
async def manual_classify(input: TextInput):
    logger.info("Bắt đầu xử lý /manual-classify")
    logger.info(f"Content gốc: {input.content}")
    
    processed_content = input.content
    logger.info(f"Content sau tiền xử lý: {processed_content}")

    try:
        conn = psycopg2.connect(**CRAWL_DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS manual_entries (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("""
            INSERT INTO manual_entries (content, url)
            VALUES (%s, %s)
            RETURNING id;
        """, (input.content, input.url))
        manual_entry_id = cursor.fetchone()[0]
        conn.commit()
        logger.info(f"Đã lưu manual_entries với ID: {manual_entry_id}")
    except Exception as e:
        logger.error(f"Lỗi khi lưu manual_entries: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi khi lưu manual_entries: {str(e)}")
    finally:
        cursor.close()
        conn.close()

    try:
        conn = psycopg2.connect(**CRAWL_DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS filtered_data (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                url TEXT,
                is_approved BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("""
            INSERT INTO filtered_data (content, url, is_approved)
            VALUES (%s, %s, %s);
        """, (input.content, input.url, True))
        conn.commit()
        logger.info("Đã lưu vào filtered_data")
    except Exception as e:
        logger.error(f"Lỗi khi lưu filtered_data: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi khi lưu filtered_data: {str(e)}")
    finally:
        cursor.close()
        conn.close()

    try:
        result = call_training_service({"content": input.content, "url": input.url})
        label = result.get("label")
        probability = result.get("probability")
        probabilities = result.get("probabilities")
        
        if not label or probability is None:
            raise ValueError("Thiếu label hoặc probability trong phản hồi từ Training Service")

        # Lưu vào training_data trong training_db
        try:
            conn = psycopg2.connect(**TRAINING_DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS training_data (
                    id SERIAL PRIMARY KEY,
                    content TEXT NOT NULL,
                    label TEXT NOT NULL,
                    probability FLOAT NOT NULL,
                    probabilities JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            cursor.execute("""
                INSERT INTO training_data (content, label, probability, probabilities)
                VALUES (%s, %s, %s, %s::jsonb);
            """, (input.content, label, probability, json.dumps(probabilities)))
            conn.commit()
            logger.info("Đã lưu kết quả phân loại thủ công vào training_data trong training_db")
        except Exception as e:
            logger.error(f"Lỗi khi lưu vào training_data: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Lỗi khi lưu vào training_data: {str(e)}")
        finally:
            cursor.close()
            conn.close()

        return {
            "message": "Bài viết đã được phân loại và lưu!",
            "label": label,
            "probability": probability,
            "probabilities": probabilities
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Lỗi khi phân loại thủ công: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi khi phân loại thủ công: {str(e)}")

@router.post("/save-classified")
async def save_classified(input: ClassifiedInput):
    try:
        conn = psycopg2.connect(**CRAWL_DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS classified_results (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                url TEXT,
                label TEXT NOT NULL,
                probability FLOAT NOT NULL,
                probabilities JSONB,
                classified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("""
            INSERT INTO classified_results (content, url, label, probability, probabilities)
            VALUES (%s, %s, %s, %s, %s);
        """, (input.content, input.url, input.label, input.probability, json.dumps(input.probabilities)))
        conn.commit()
        logger.info("Đã lưu kết quả phân loại vào classified_results")
    except Exception as e:
        logger.error(f"Lỗi khi lưu classified_results: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi khi lưu classified_results: {str(e)}")
    finally:
        cursor.close()
        conn.close()
    return {"message": "Kết quả phân loại đã được lưu"}

@router.get("/classified-results")
async def get_classified_results(limit: int = 100):
    try:
        conn = psycopg2.connect(**CRAWL_DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT content, url, label, probability, probabilities
            FROM classified_results
            ORDER BY classified_at DESC
            LIMIT %s;
        """, (limit,))
        rows = cursor.fetchall()
        logger.info(f"Trả về {len(rows)} bản ghi từ classified_results")
        cursor.close()
        conn.close()
        return {
            "classified_results": [
                {
                    "content": row[0],
                    "url": row[1],
                    "label": row[2],
                    "probability": row[3],
                    "probabilities": row[4]
                } for row in rows
            ]
        }
    except Exception as e:
        logger.error(f"Lỗi khi lấy classified_results: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy classified_results: {str(e)}")