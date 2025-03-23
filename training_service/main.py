from fastapi import FastAPI
from config import TRAINING_SERVICE_PORT, PHOBERT_MODEL_NAME, NUM_CLASSES, MODEL_PATH
from routes import process_data_route
import torch
from transformers import AutoTokenizer, AutoModel
from model import ConvNet, extract_text_features_batch

app = FastAPI(title="Training Service")

if __name__ == "__main__":
    from multiprocessing import freeze_support
    freeze_support()
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    print("Đang tải PhoBERT...")
    try:
        tokenizer = AutoTokenizer.from_pretrained(PHOBERT_MODEL_NAME)
        phobert_model = AutoModel.from_pretrained(PHOBERT_MODEL_NAME).to(device)
        print("Đã tải PhoBERT thành công!")
    except Exception as e:
        print(f"Lỗi khi tải PhoBERT: {e}")
        raise

    print("Đang tải ConvNet model...")
    dummy_features = extract_text_features_batch(["Dummy text"], device, phobert_model, tokenizer)
    input_size = dummy_features.shape[1]
    model = ConvNet(input_size=input_size, output_size=NUM_CLASSES).to(device)
    try:
        model.load_state_dict(torch.load(MODEL_PATH, map_location=device, weights_only=True))
        print("Đã tải mô hình ConvNet thành công từ", MODEL_PATH)
    except Exception as e:
        print(f"Lỗi khi tải mô hình ConvNet: {e}")
        raise

    router = process_data_route(model, device, phobert_model, tokenizer)
    app.include_router(router)

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=TRAINING_SERVICE_PORT)