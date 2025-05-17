import psycopg2
from config import CRAWL_DB_CONFIG, TRAINING_DB_CONFIG, DASHBOARD_DB_CONFIG
from datetime import datetime, timedelta
from psycopg2.extras import execute_batch
import logging

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

def connect_dashboard_db():
    try:
        conn = psycopg2.connect(**DASHBOARD_DB_CONFIG)
        logger.info("Kết nối thành công tới dashboard_db")
        return conn
    except Exception as e:
        logger.error(f"Lỗi khi kết nối dashboard_db: {str(e)}")
        raise

def create_tables():
    conn = connect_dashboard_db()
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
        CREATE TABLE IF NOT EXISTS classified_results (
            id SERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            url TEXT,
            label TEXT NOT NULL,
            probability FLOAT NOT NULL,
            classified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
        CREATE TABLE IF NOT EXISTS fake_social_news (
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
    conn.commit()
    cursor.close()
    conn.close()
    logger.info("Đã tạo các bảng trong dashboard_db")

def save_manual_entry(content, url):
    conn = connect_dashboard_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO manual_entries (content, url) VALUES (%s, %s) RETURNING id;", (content, url))
        entry_id = cursor.fetchone()[0]
        conn.commit()
        logger.info(f"Đã lưu manual_entry với id={entry_id}")
        return entry_id
    except Exception as e:
        logger.error(f"Lỗi khi lưu manual_entry: {str(e)}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

def save_classified_result(content, url, label, probability):
    conn = connect_dashboard_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO classified_results (content, url, label, probability)
            VALUES (%s, %s, %s, %s);
        """, (content, url, label, probability))
        conn.commit()
        logger.info(f"Đã lưu classified_result: {label}, probability={probability}")
    except Exception as e:
        logger.error(f"Lỗi khi lưu classified_result: {str(e)}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

def fetch_display_data(limit):
    conn = connect_dashboard_db()
    cursor = conn.cursor()
    try:
        ten_minutes_ago = datetime.now() - timedelta(minutes=10)
        cursor.execute("""
            SELECT content, url, label, probability, probabilities
            FROM display_data
            WHERE processed_at >= %s
            ORDER BY processed_at DESC
            LIMIT %s;
        """, (ten_minutes_ago, limit))
        rows = cursor.fetchall()
        logger.info(f"Lấy được {len(rows)} bản ghi từ display_data")
        return [{"content": row[0], "url": row[1], "label": row[2], "probability": row[3], "probabilities": row[4]} for row in rows]
    except Exception as e:
        logger.error(f"Lỗi khi lấy display_data: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()

def fetch_normal_news(limit):
    conn = connect_dashboard_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT content, url, probability FROM normal_news ORDER BY processed_at DESC LIMIT %s;", (limit,))
        rows = cursor.fetchall()
        logger.info(f"Lấy được {len(rows)} bản ghi từ normal_news")
        return [{"content": row[0], "url": row[1], "probability": row[2]} for row in rows]
    except Exception as e:
        logger.error(f"Lỗi khi lấy normal_news: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()

def fetch_fake_social_news(limit):
    conn = connect_dashboard_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT content, url, probability FROM fake_social_news ORDER BY processed_at DESC LIMIT %s;", (limit,))
        rows = cursor.fetchall()
        logger.info(f"Lấy được {len(rows)} bản ghi từ fake_social_news")
        return [{"content": row[0], "url": row[1], "probability": row[2]} for row in rows]
    except Exception as e:
        logger.error(f"Lỗi khi lấy fake_social_news: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()

def fetch_fake_political_news(limit):
    conn = connect_dashboard_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT content, url, probability FROM fake_political_news ORDER BY processed_at DESC LIMIT %s;", (limit,))
        rows = cursor.fetchall()
        logger.info(f"Lấy được {len(rows)} bản ghi từ fake_political_news")
        return [{"content": row[0], "url": row[1], "probability": row[2]} for row in rows]
    except Exception as e:
        logger.error(f"Lỗi khi lấy fake_political_news: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()

def fetch_raw_fanpage_facebook(limit):
    conn = connect_crawl_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT content
            FROM raw_fanpage_facebook
            ORDER BY id DESC
            LIMIT %s;
        """, (limit,))
        rows = cursor.fetchall()
        logger.info(f"Lấy được {len(rows)} bản ghi từ raw_fanpage_facebook")
        return [{"content": row[0]} for row in rows]
    except Exception as e:
        logger.error(f"Lỗi khi lấy raw_fanpage_facebook: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()

def fetch_stats(start_date=None, end_date=None):
    conn = connect_dashboard_db()
    cursor = conn.cursor()
    try:
        where_clause = ""
        params = []
        if start_date:
            where_clause += " WHERE processed_at >= %s"
            params.append(start_date)
        if end_date:
            where_clause += " AND" if "WHERE" in where_clause else " WHERE"
            where_clause += " processed_at <= %s"
            params.append(end_date)

        cursor.execute(f"""
            SELECT DATE(processed_at) as date, COUNT(*) as count
            FROM display_data
            {where_clause}
            GROUP BY DATE(processed_at)
            ORDER BY date;
        """, params)
        time_stats = [{"date": row[0].isoformat(), "count": row[1]} for row in cursor.fetchall()]

        cursor.execute(f"SELECT COUNT(*) FROM display_data {where_clause};", params)
        total_articles = cursor.fetchone()[0]
        
        cursor.execute(f"SELECT COUNT(*) FROM normal_news {where_clause};", params)
        normal_count = cursor.fetchone()[0]
        cursor.execute(f"SELECT COUNT(*) FROM fake_social_news {where_clause};", params)
        fake_social_count = cursor.fetchone()[0]
        cursor.execute(f"SELECT COUNT(*) FROM fake_political_news {where_clause};", params)
        fake_political_count = cursor.fetchone()[0]

        ratios = {
            "normal_news": round((normal_count / total_articles * 100) if total_articles > 0 else 0, 2),
            "fake_social_news": round((fake_social_count / total_articles * 100) if total_articles > 0 else 0, 2),
            "fake_political_news": round((fake_political_count / total_articles * 100) if total_articles > 0 else 0, 2)
        }

        logger.info(f"Lấy được thống kê: total_articles={total_articles}, ratios={ratios}")
        return {"time_stats": time_stats, "ratios": ratios, "total_articles": total_articles}
    except Exception as e:
        logger.error(f"Lỗi khi lấy thống kê: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()