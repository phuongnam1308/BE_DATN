import psycopg2
from config import CRAWL_DB_CONFIG, TRAINING_DB_CONFIG

def connect_crawl_db():
    return psycopg2.connect(**CRAWL_DB_CONFIG)

def connect_training_db():
    return psycopg2.connect(**TRAINING_DB_CONFIG)

def create_tables():
    conn = connect_training_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS training_data (
            id SERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            label TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS display_data (
            id SERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            url TEXT NOT NULL,
            label TEXT NOT NULL,
            probability FLOAT NOT NULL,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS normal_news (
            id SERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            url TEXT NOT NULL,
            probability FLOAT NOT NULL,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fake_political_news (
            id SERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            url TEXT NOT NULL,
            probability FLOAT NOT NULL,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fake_social_news (
            id SERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            url TEXT NOT NULL,
            probability FLOAT NOT NULL,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    conn.commit()
    cursor.close()
    conn.close()

def fetch_unprocessed_data(batch_size=100):
    conn = connect_crawl_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, content, url
        FROM clean_fanpage_facebook
        WHERE process = FALSE
        LIMIT %s;
    """, (batch_size,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [{"id": row[0], "content": row[1], "url": row[2]} for row in rows]

def mark_as_processed(post_ids):
    conn = connect_crawl_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE clean_fanpage_facebook
        SET process = TRUE
        WHERE id = ANY(%s);
    """, (post_ids,))
    conn.commit()
    cursor.close()
    conn.close()

def save_to_training_data(items):
    conn = connect_training_db()
    cursor = conn.cursor()
    cursor.executemany("""
        INSERT INTO training_data (content, label)
        VALUES (%s, %s);
    """, [(item["content"], item["label"]) for item in items])
    conn.commit()
    cursor.close()
    conn.close()

def save_to_display_data(items):
    conn = connect_training_db()
    cursor = conn.cursor()
    cursor.executemany("""
        INSERT INTO display_data (content, url, label, probability)
        VALUES (%s, %s, %s, %s);
    """, [(item["content"], item["url"], item["label"], item["probability"]) for item in items])
    conn.commit()
    cursor.close()
    conn.close()

def save_to_category_tables(items):
    conn = connect_training_db()
    cursor = conn.cursor()
    
    normal_items = [item for item in items if item["label"] == "Tin thường"]
    fake_political_items = [item for item in items if item["label"] == "Tin giả về chính trị"]
    fake_social_items = [item for item in items if item["label"] == "Tin giả về đời sống xã hội"]
    
    if normal_items:
        cursor.executemany("""
            INSERT INTO normal_news (content, url, probability)
            VALUES (%s, %s, %s);
        """, [(item["content"], item["url"], item["probability"]) for item in normal_items])
    
    if fake_political_items:
        cursor.executemany("""
            INSERT INTO fake_political_news (content, url, probability)
            VALUES (%s, %s, %s);
        """, [(item["content"], item["url"], item["probability"]) for item in fake_political_items])
    
    if fake_social_items:
        cursor.executemany("""
            INSERT INTO fake_social_news (content, url, probability)
            VALUES (%s, %s, %s);
        """, [(item["content"], item["url"], item["probability"]) for item in fake_social_items])
    
    conn.commit()
    cursor.close()
    conn.close()