from fastapi import FastAPI
import httpx

app = FastAPI()

BASE_URLS = {
    "crawl": "http://127.0.0.1:8001",
    "training": "http://127.0.0.1:8002",
    "dashboard": "http://127.0.0.1:8003",
    "admin": "http://127.0.0.1:8004",
}

@app.get("/")
def read_root():
    return {"message": "API Gateway is running!"}

@app.post("/crawl/add_post/")
async def add_post(title: str, content: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URLS['crawl']}/add_post/", params={"title": title, "content": content})
    return response.json()
