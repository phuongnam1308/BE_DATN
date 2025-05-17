from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import TRAINING_SERVICE_PORT, PHOBERT_MODEL_NAME, NUM_CLASSES, MODEL_PATH
from routes import process_data_route
from model import ConvNet, load_phobert_and_tokenizer
import torch
import logging
from multiprocessing import freeze_support

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Training Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def initialize_training_service():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Sử dụng thiết bị: {device}")

    phobert_model, tokenizer = load_phobert_and_tokenizer(PHOBERT_MODEL_NAME)
    model = ConvNet(num_classes=NUM_CLASSES).to(device)
    try:
        model.load_state_dict(torch.load(MODEL_PATH, map_location=device, weights_only=True))
        model.eval()
        logger.info(f"Đã tải mô hình từ {MODEL_PATH}")
    except Exception as e:
        logger.error(f"Lỗi khi tải mô hình: {str(e)}")
        raise

    app.include_router(process_data_route(model, device, phobert_model, tokenizer))
    logger.info("Router đã được đăng ký thành công!")

if __name__ == "__main__":
    freeze_support()
    initialize_training_service()
    import uvicorn
    logger.info(f"Khởi động Training Service trên cổng {TRAINING_SERVICE_PORT}")
    uvicorn.run(app, host="0.0.0.0", port=TRAINING_SERVICE_PORT)