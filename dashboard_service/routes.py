from fastapi import APIRouter, HTTPException, Query
from database import create_tables, save_manual_entry, save_classified_result, fetch_display_data, fetch_normal_news, fetch_fake_social_news, fetch_fake_political_news, fetch_raw_fanpage_facebook, fetch_stats, connect_training_db
import requests
from config import TRAINING_SERVICE_URL
from models import ManualEntry
from datetime import date

router = APIRouter()

@router.post("/manual-classify")
async def manual_classify(entry: ManualEntry):
    try:
        entry_id = save_manual_entry(entry.content, entry.url)
        payload = {"content": entry.content, "url": entry.url}
        response = requests.post(TRAINING_SERVICE_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        if "processed_data" in result and len(result["processed_data"]) > 0:
            classified = result["processed_data"][0]
            label = classified["label"]
            probability = classified["probability"]
            save_classified_result(entry.content, entry.url, label, probability)
            return {"message": "Bài viết đã được phân loại và lưu!", "entry_id": entry_id, "label": label, "probability": probability}
        else:
            raise ValueError("Không nhận được kết quả từ training_service")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi phân loại: {str(e)}")

@router.get("/display-data")
async def get_display_data(limit: int = 100):
    try:
        data = fetch_display_data(limit)
        return {"display_data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy display_data: {str(e)}")

@router.get("/normal-news")
async def get_normal_news(limit: int = 100):
    try:
        data = fetch_normal_news(limit)
        return {"normal_news": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy normal_news: {str(e)}")

@router.get("/fake-social-news")
async def get_fake_social_news(limit: int = 100):
    try:
        data = fetch_fake_social_news(limit)
        return {"fake_social_news": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy fake_social_news: {str(e)}")

@router.get("/fake-political-news")
async def get_fake_political_news(limit: int = 100):
    try:
        data = fetch_fake_political_news(limit)
        return {"fake_political_news": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy fake_political_news: {str(e)}")

@router.get("/raw-fanpage-facebook")
async def get_raw_fanpage_facebook(limit: int = 100):
    try:
        data = fetch_raw_fanpage_facebook(limit)
        return {"raw_fanpage_facebook": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy raw_fanpage_facebook: {str(e)}")

@router.get("/stats")
async def get_stats(start_date: date | None = None, end_date: date | None = None):
    try:
        stats = fetch_stats(start_date, end_date)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy thống kê: {str(e)}")

@router.get("/search-articles")
async def search_articles(query: str = Query(..., min_length=3), limit: int = 100):
    try:
        conn = connect_training_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT content, url, label, probability
            FROM display_data
            WHERE content ILIKE %s
            ORDER BY processed_at DESC
            LIMIT %s;
        """, (f"%{query}%", limit))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return {
            "results": [{"content": row[0], "url": row[1], "label": row[2], "probability": row[3]} for row in rows]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi tìm kiếm: {str(e)}")

@router.get("/compare-articles")
async def compare_articles(id1: int | None = None, id2: int | None = None):
    try:
        conn = connect_training_db()
        cursor = conn.cursor()

        if id1 is not None and id2 is not None:
            # So sánh 2 bài cụ thể
            cursor.execute("""
                SELECT content, label, probability
                FROM display_data
                WHERE id IN (%s, %s);
            """, (id1, id2))
            rows = cursor.fetchall()
            
            if len(rows) != 2:
                raise HTTPException(status_code=404, detail="Không tìm thấy một hoặc cả hai bài viết")
            
            article1 = {"content": rows[0][0], "label": rows[0][1], "probability": rows[0][2]}
            article2 = {"content": rows[1][0], "label": rows[1][1], "probability": rows[1][2]}
            
            comparison = {}
            if article1["label"] == article2["label"]:
                ratio = article1["probability"] / article2["probability"] if article2["probability"] > 0 else float('inf')
                comparison["probability_ratio"] = round(ratio, 2)
                comparison["note"] = f"Bài {id1} có xác suất {comparison['probability_ratio']} lần so với bài {id2}"
            else:
                comparison["note"] = "Hai bài thuộc loại khác nhau, không thể so sánh tỉ lệ probability"

            cursor.close()
            conn.close()
            return {
                "article1": {"id": id1, **article1},
                "article2": {"id": id2, **article2},
                "comparison": comparison
            }
        else:
            # So sánh tổng quát giữa các nhãn
            cursor.execute("""
                SELECT label, COUNT(*) as count, AVG(probability) as avg_probability
                FROM display_data
                GROUP BY label;
            """)
            label_stats = cursor.fetchall()

            if not label_stats:
                raise HTTPException(status_code=404, detail="Không có dữ liệu để so sánh")

            stats = {row[0]: {"count": row[1], "avg_probability": round(row[2], 2)} for row in label_stats}
            
            # Tính tỉ lệ giữa các nhãn dựa trên avg_probability
            comparisons = {}
            labels = list(stats.keys())
            for i in range(len(labels)):
                for j in range(i + 1, len(labels)):
                    label1, label2 = labels[i], labels[j]
                    if stats[label2]["avg_probability"] > 0:
                        ratio = stats[label1]["avg_probability"] / stats[label2]["avg_probability"]
                        comparisons[f"{label1}_vs_{label2}"] = {
                            "ratio": round(ratio, 2),
                            "note": f"{label1} có xác suất trung bình {round(ratio, 2)} lần so với {label2}"
                        }

            cursor.close()
            conn.close()
            return {
                "label_stats": stats,
                "comparisons": comparisons
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi so sánh: {str(e)}")