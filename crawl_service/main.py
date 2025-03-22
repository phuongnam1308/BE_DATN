from fastapi import FastAPI
from routes import router
from config import CRAWL_SERVICE_PORT

app = FastAPI(title="Crawl Service")
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=CRAWL_SERVICE_PORT)