from fastapi import APIRouter, HTTPException
from database import fetch_unprocessed_data, mark_as_processed, save_to_training_data, save_to_display_data, save_to_category_tables, create_tables
from model import predict_news_type_batch
from pydantic import BaseModel
import logging
import json
from config import SUSPICIOUS_URLS, TRUSTED_URLS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_data_route(model, device, phobert_model, tokenizer):
    router = APIRouter()

    class ManualContent(BaseModel):
        content: str
        url: str | None = None

    @router.post("/process")
    async def process_data(save_to_training: bool = False, batch_size: int = 100):
        try:
            logger.info("Bắt đầu xử lý dữ liệu từ crawl_db")
            create_tables()
            total_processed = 0
            
            while True:
                unprocessed_data = fetch_unprocessed_data(batch_size)
                if not unprocessed_data:
                    logger.info("Không còn dữ liệu chưa xử lý trong clean_fanpage_facebook")
                    break
                
                texts = [item["content"] for item in unprocessed_data]
                is_suspicious_list = [item["is_suspicious"] for item in unprocessed_data]
                is_trusted_list = [item["is_trusted"] for item in unprocessed_data]
                logger.info(f"Đang phân loại {len(texts)} bài viết")
                predicted_labels, probabilities = predict_news_type_batch(
                    texts, model, device, phobert_model, tokenizer, is_suspicious_list, is_trusted_list
                )
                
                processed_data = []
                display_items = []
                training_items = []
                category_items = []
                for i, item in enumerate(unprocessed_data):
                    probability = float(probabilities[i][{"Tin thường": 0, "Tin giả về đời sống xã hội": 1, "Tin giả về chính trị": 2}[predicted_labels[i]]])
                    probabilities_dict = {
                        "Tin thường": float(probabilities[i][0]),
                        "Tin giả về đời sống xã hội": float(probabilities[i][1]),
                        "Tin giả về chính trị": float(probabilities[i][2])
                    }
                    processed_item = {
                        "id": item["id"],
                        "content": item["content"],
                        "label": predicted_labels[i]
                    }
                    display_item = {
                        "content": item["content"],
                        "url": item["url"],
                        "label": predicted_labels[i],
                        "probability": probability,
                        "probabilities": probabilities_dict
                    }
                    category_item = {
                        "content": item["content"],
                        "url": item["url"],
                        "label": predicted_labels[i],
                        "probability": probability
                    }
                    training_item = {
                        "content": item["content"],
                        "label": predicted_labels[i],
                        "probability": probability,
                        "probabilities": probabilities_dict
                    }
                    processed_data.append(processed_item)
                    display_items.append(display_item)
                    category_items.append(category_item)
                    training_items.append(training_item)
                
                logger.info(f"Lưu {len(display_items)} bản ghi vào display_data và category_tables")
                logger.info(f"Lưu {len(training_items)} bản ghi vào training_data")
                save_to_display_data(display_items)
                save_to_category_tables(category_items)
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
            create_tables()
            
            texts = [content.content]
            is_suspicious = content.url and any(suspicious_url in content.url for suspicious_url in SUSPICIOUS_URLS)
            is_trusted = content.url and any(trusted_url in content.url for trusted_url in TRUSTED_URLS)
            logger.info(f"Bắt đầu dự đoán với predict_news_type_batch, is_suspicious={is_suspicious}, is_trusted={is_trusted}")
            predicted_labels, probabilities = predict_news_type_batch(
                texts, model, device, phobert_model, tokenizer, [is_suspicious], [is_trusted]
            )
            
            label = predicted_labels[0]
            probability = float(probabilities[0][{"Tin thường": 0, "Tin giả về đời sống xã hội": 1, "Tin giả về chính trị": 2}[label]])
            probabilities_dict = {
                "Tin thường": float(probabilities[0][0]),
                "Tin giả về đời sống xã hội": float(probabilities[0][1]),
                "Tin giả về chính trị": float(probabilities[0][2])
            }
            
            # Lưu vào training_data trong training_db
            training_item = [{
                "content": content.content,
                "label": label,
                "probability": probability,
                "probabilities": probabilities_dict
            }]
            save_to_training_data(training_item)
            
            result = {
                "content": content.content,
                "url": content.url,
                "label": label,
                "probability": probability,
                "probabilities": probabilities_dict
            }
            
            logger.info(f"Dự đoán hoàn tất: label={label}, probability={probability}")
            logger.info("Hoàn tất phân loại thủ công")
            return {
                "message": "Bài viết đã được phân loại!",
                "label": label,
                "probability": probability,
                "probabilities": probabilities_dict
            }
        except Exception as e:
            logger.error(f"Lỗi khi phân loại thủ công: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Lỗi khi phân loại thủ công: {str(e)}")
    
    return router