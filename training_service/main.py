from fastapi import FastAPI
from database import connect_db, create_table

app = FastAPI()

@app.post("/train/")
def train_model():
    create_table()
    return {"status": "training started"}
