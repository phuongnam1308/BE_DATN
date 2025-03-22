import psycopg2
import re
from config import DB_CONFIG

def connect_db():
    return psycopg2.connect(**DB_CONFIG)

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()
    
    # Tạo bảng raw_fanpage_facebook
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS raw_fanpage_facebook (
            id SERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Tạo bảng clean_fanpage_facebook
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clean_fanpage_facebook (
            id SERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            url TEXT NOT NULL,
            data_crawl TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            process BOOLEAN DEFAULT FALSE
        );
    """)
    
    conn.commit()
    cursor.close()
    conn.close()

def save_raw_to_db(posts):
    conn = connect_db()
    cursor = conn.cursor()
    for post in posts:
        cursor.execute("INSERT INTO raw_fanpage_facebook (content) VALUES (%s) ON CONFLICT DO NOTHING;", (post,))
    conn.commit()
    cursor.close()
    conn.close()

def preprocess_for_phobert(text):
    # Loại bỏ ký tự đặc biệt không cần thiết, giữ lại chữ cái, số, dấu câu cơ bản
    text = re.sub(r'[^\w\s.,!?]', '', text)
    # Chuẩn hóa khoảng trắng
    text = ' '.join(text.split())
    # Giữ nguyên tiếng Việt có dấu, không chuyển lowercase (PhoBERT cần giữ nguyên)
    return text

def save_clean_to_db(posts, url):
    conn = connect_db()
    cursor = conn.cursor()
    for post in posts:
        clean_content = preprocess_for_phobert(post)
        cursor.execute("""
            INSERT INTO clean_fanpage_facebook (content, url, process)
            VALUES (%s, %s, %s);
        """, (clean_content, url, False))
    conn.commit()
    cursor.close()
    conn.close()