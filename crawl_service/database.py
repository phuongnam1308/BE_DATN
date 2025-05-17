import psycopg2
import re
from config import CRAWL_DB_CONFIG
import logging
from psycopg2.extras import execute_batch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def connect_db():
    try:
        conn = psycopg2.connect(**CRAWL_DB_CONFIG)
        logger.info("Kết nối thành công tới crawl_db")
        return conn
    except Exception as e:
        logger.error(f"Lỗi khi kết nối crawl_db: {str(e)}")
        raise

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS raw_fanpage_facebook (
            id SERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clean_fanpage_facebook (
            id SERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            url TEXT NOT NULL,
            data_crawl TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            process BOOLEAN DEFAULT FALSE,
            is_suspicious BOOLEAN DEFAULT FALSE,
            is_trusted BOOLEAN DEFAULT FALSE
        );
    """)
    
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
        CREATE TABLE IF NOT EXISTS manual_entries (
            id SERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS filtered_data (
            id SERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            url TEXT,
            is_approved BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    logger.info("Đã tạo các bảng trong crawl_db")

def save_raw_to_db(posts):
    conn = connect_db()
    cursor = conn.cursor()
    query = "INSERT INTO raw_fanpage_facebook (content) VALUES (%s) ON CONFLICT DO NOTHING;"
    execute_batch(cursor, query, [(post["text"],) for post in posts])
    conn.commit()
    cursor.close()
    conn.close()
    logger.info(f"Đã lưu {len(posts)} bài viết vào raw_fanpage_facebook")

def preprocess_for_phobert(text):
    text = re.sub(r'[^\w\s.,!?]', '', text)
    text = ' '.join(text.split())
    return text

def save_clean_to_db(posts, url):
    conn = connect_db()
    cursor = conn.cursor()
    query = """
        INSERT INTO clean_fanpage_facebook (content, url, process, is_suspicious, is_trusted)
        VALUES (%s, %s, %s, %s, %s);
    """
    execute_batch(cursor, query, [
        (preprocess_for_phobert(post["text"]), url, False, post["is_suspicious"], post["is_trusted"])
        for post in posts
    ])
    conn.commit()
    cursor.close()
    conn.close()
    logger.info(f"Đã lưu {len(posts)} bài viết vào clean_fanpage_facebook")

def save_filtered_data(posts, url):
    conn = connect_db()
    cursor = conn.cursor()
    query = """
        INSERT INTO filtered_data (content, url, is_approved)
        VALUES (%s, %s, %s);
    """
    execute_batch(cursor, query, [
        (preprocess_for_phobert(post["text"]), url, False)
        for post in posts
    ])
    conn.commit()
    cursor.close()
    conn.close()
    logger.info(f"Đã lưu {len(posts)} bài viết vào filtered_data")