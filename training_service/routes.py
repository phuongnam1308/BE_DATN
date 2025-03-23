from fastapi import APIRouter, HTTPException
from database import fetch_unprocessed_data, mark_as_processed, save_to_training_data, save_to_display_data, save_to_category_tables, create_tables
from model import predict_news_type_batch
from pydantic import BaseModel
import logging

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class ManualContent(BaseModel):
    content: str
    url: str | None = None

def process_data_route(model, device, phobert_model, tokenizer):
    @router.post("/process")
    async def process_data(save_to_training: bool = False, batch_size: int = 100):
        try:
            logger.info("Bắt đầu xử lý dữ liệu từ crawl_db")
            create_tables()
            total_processed = 0
            
            while True:
                unprocessed_data = fetch_unprocessed_data(batch_size)
                if not unprocessed_data:
                    break
                
                texts = [item["content"] for item in unprocessed_data]
                predicted_labels, probabilities = predict_news_type_batch(texts, model, device, phobert_model, tokenizer)
                
                processed_data = []
                display_items = []
                training_items = []
                category_items = []
                for i, item in enumerate(unprocessed_data):
                    probability = float(probabilities[i][{"Tin thường": 0, "Tin giả về đời sống xã hội": 1, "Tin giả về chính trị": 2}[predicted_labels[i]]])
                    processed_item = {
                        "id": item["id"],
                        "content": item["content"],
                        "label": predicted_labels[i]
                    }
                    display_item = {
                        "content": item["content"],
                        "url": item["url"],
                        "label": predicted_labels[i],
                        "probability": probability
                    }
                    category_item = {
                        "content": item["content"],
                        "url": item["url"],
                        "label": predicted_labels[i],
                        "probability": probability
                    }
                    processed_data.append(processed_item)
                    display_items.append(display_item)
                    category_items.append(category_item)
                    if save_to_training:
                        training_items.append({
                            "content": item["content"],
                            "label": predicted_labels[i]
                        })
                
                save_to_display_data(display_items)
                save_to_category_tables(category_items)
                if save_to_training:
                    save_to_training_data(training_items)
                
                post_ids = [item["id"] for item in unprocessed_data]
                mark_as_processed(post_ids)
                total_processed += len(processed_data)
            
            logger.info(f"Hoàn tất xử lý {total_processed} bản ghi")
            return {
                "message": f"Đã xử lý toàn bộ {total_processed} bản ghi từ crawl_db!"
            }
        except Exception as e:
            logger.error(f"Lỗi khi xử lý: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Lỗi khi xử lý: {str(e)}")

    @router.post("/classify-manual")
    async def classify_manual(content: ManualContent):
        try:
            logger.info(f"Nhận yêu cầu phân loại thủ công: {content.content[:50]}...")
            create_tables()  # Đảm bảo bảng tồn tại
            
            texts = [content.content]
            logger.info("Bắt đầu dự đoán với predict_news_type_batch")
            predicted_labels, probabilities = predict_news_type_batch(texts, model, device, phobert_model, tokenizer)
            
            label = predicted_labels[0]
            probability = float(probabilities[0][{"Tin thường": 0, "Tin giả về đời sống xã hội": 1, "Tin giả về chính trị": 2}[label]])
            
            result = {
                "content": content.content,
                "url": content.url,
                "label": label,
                "probability": probability
            }
            
            logger.info(f"Dự đoán hoàn tất: label={label}, probability={probability}")
            logger.info("Lưu vào display_data")
            display_item = [result]
            save_to_display_data(display_item)
            
            logger.info("Lưu vào category_tables")
            save_to_category_tables(display_item)
            
            logger.info("Hoàn tất phân loại thủ công")
            return {
                "message": "Đã phân loại bài viết thủ công!",
                "processed_data": [result]
            }
        except Exception as e:
            logger.error(f"Lỗi khi phân loại thủ công: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Lỗi khi phân loại thủ công: {str(e)}")
    
    return router