from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router
from config import DASHBOARD_SERVICE_PORT
from database import create_tables
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Dashboard Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

create_tables()
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    from multiprocessing import freeze_support
    freeze_support()
    logger.info(f"Khởi động Dashboard Service trên cổng {DASHBOARD_SERVICE_PORT}")
    uvicorn.run(app, host="0.0.0.0", port=DASHBOARD_SERVICE_PORT)