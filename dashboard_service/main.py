from fastapi import FastAPI
from routes import router
from config import DASHBOARD_SERVICE_PORT
from database import create_tables

app = FastAPI(title="Dashboard Service")

create_tables()
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    from multiprocessing import freeze_support
    freeze_support()
    uvicorn.run(app, host="0.0.0.0", port=DASHBOARD_SERVICE_PORT)