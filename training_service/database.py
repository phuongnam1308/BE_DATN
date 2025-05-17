import psycopg2
from config import CRAWL_DB_CONFIG, TRAINING_DB_CONFIG
import logging
import json
from psycopg2.extras import execute_batch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def connect_crawl_db():
    try:
        conn = psycopg2.connect(**CRAWL_DB_CONFIG)
        logger.info("Kết nối thành công tới crawl_db")
        return conn
    except Exception as e:
        logger.error(f"Lỗi khi kết nối crawl_db: {str(e)}")
        raise

def connect_training_db():
    try:
        conn = psycopg2.connect(**TRAINING_DB_CONFIG)
        logger.info("Kết nối thành công tới training_db")
        return conn
    except Exception as e:
        logger.error(f"Lỗi khi kết nối training_db: {str(e)}")
        raise

def create_tables():
    conn = connect_training_db()
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
        CREATE TABLE IF NOT EXISTS display_data (
            id SERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            url TEXT,
            label TEXT NOT NULL,
            probability FLOAT NOT NULL,
            probabilities JSONB,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS normal_news (
            id SERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            url TEXT,
            probability FLOAT NOT NULL,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fake_political_news (
            id SERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            url TEXT,
            probability FLOAT NOT NULL,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fake_social_news (
            id SERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            url TEXT,
            probability FLOAT NOT NULL,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    logger.info("Đã tạo các bảng trong training_db")

def fetch_unprocessed_data(batch_size=100):
    conn = connect_crawl_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, content, url, is_suspicious, is_trusted
        FROM clean_fanpage_facebook
        WHERE process = FALSE
        LIMIT %s;
    """, (batch_size,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    logger.info(f"Lấy được {len(rows)} bản ghi chưa xử lý từ clean_fanpage_facebook")
    return [{"id": row[0], "content": row[1], "url": row[2], "is_suspicious": row[3], "is_trusted": row[4]} for row in rows]

def mark_as_processed(post_ids):
    conn = connect_crawl_db()
    cursor = conn.cursor()
    query = """
        UPDATE clean_fanpage_facebook
        SET process = TRUE
        WHERE id = ANY(%s);
    """
    execute_batch(cursor, query, [(post_ids,)])
    conn.commit()
    cursor.close()
    conn.close()
    logger.info(f"Đã đánh dấu {len(post_ids)} bài viết là processed")

def save_to_training_data(items):
    conn = connect_training_db()
    cursor = conn.cursor()
    query = """
        INSERT INTO training_data (content, label, probability, probabilities)
        VALUES (%s, %s, %s, %s::jsonb);
    """
    execute_batch(cursor, query, [(item["content"], item["label"], item["probability"], json.dumps(item.get("probabilities", {}))) for item in items])
    conn.commit()
    cursor.close()
    conn.close()
    logger.info(f"Đã lưu {len(items)} bản ghi vào training_data")

def save_to_display_data(items):
    conn = connect_training_db()
    cursor = conn.cursor()
    try:
        query = """
            INSERT INTO display_data (content, url, label, probability, probabilities)
            VALUES (%s, %s, %s, %s, %s::jsonb);
        """
        execute_batch(cursor, query, [
            (item["content"], item["url"], item["label"], item["probability"], json.dumps(item.get("probabilities", {})))
            for item in items
        ])
        conn.commit()
        logger.info(f"Đã lưu {len(items)} bản ghi vào display_data trong training_db")
    except Exception as e:
        logger.error(f"Lỗi khi lưu vào display_data: {str(e)}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

def save_to_category_tables(items):
    conn = connect_training_db()
    cursor = conn.cursor()
    try:
        normal_items = [item for item in items if item["label"] == "Tin thường"]
        fake_political_items = [item for item in items if item["label"] == "Tin giả về chính trị"]
        fake_social_items = [item for item in items if item["label"] == "Tin giả về đời sống xã hội"]
        
        if normal_items:
            query = """
                INSERT INTO normal_news (content, url, probability)
                VALUES (%s, %s, %s);
            """
            execute_batch(cursor, query, [
                (item["content"], item["url"], item["probability"])
                for item in normal_items
            ])
            logger.info(f"Đã lưu {len(normal_items)} bản ghi vào normal_news trong training_db")
        
        if fake_political_items:
            query = """
                INSERT INTO fake_political_news (content, url, probability)
                VALUES (%s, %s, %s);
            """
            execute_batch(cursor, query, [
                (item["content"], item["url"], item["probability"])
                for item in fake_political_items
            ])
            logger.info(f"Đã lưu {len(fake_political_items)} bản ghi vào fake_political_news trong training_db")
        
        if fake_social_items:
            query = """
                INSERT INTO fake_social_news (content, url, probability)
                VALUES (%s, %s, %s);
            """
            execute_batch(cursor, query, [
                (item["content"], item["url"], item["probability"])
                for item in fake_social_items
            ])
            logger.info(f"Đã lưu {len(fake_social_items)} bản ghi vào fake_social_news trong training_db")
        
        conn.commit()
    except Exception as e:
        logger.error(f"Lỗi khi lưu vào category_tables: {str(e)}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()