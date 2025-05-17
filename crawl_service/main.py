from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import CRAWL_SERVICE_PORT
from routes import router

app = FastAPI(title="Crawl Service")

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    from multiprocessing import freeze_support
    freeze_support()
    uvicorn.run(app, host="0.0.0.0", port=CRAWL_SERVICE_PORT)