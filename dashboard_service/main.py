from fastapi import FastAPI
from database import connect_db

app = FastAPI()

@app.get("/dashboard/")
def get_dashboard():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dataset_training;")
    results = cursor.fetchall()
    conn.close()
    return {"data": results}
