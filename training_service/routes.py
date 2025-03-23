from fastapi import APIRouter, HTTPException
from database import fetch_unprocessed_data, mark_as_processed, save_to_training_data, save_to_display_data, save_to_category_tables, create_tables
from model import predict_news_type_batch

router = APIRouter()

def process_data_route(model, device, phobert_model, tokenizer):
    @router.post("/process")
    async def process_data(save_to_training: bool = False, batch_size: int = 100):
        try:
            create_tables()
            total_processed = 0
            
            while True:
                unprocessed_data = fetch_unprocessed_data(batch_size)
                if not unprocessed_data:
                    break  # Thoát khi không còn dữ liệu
                
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
            
            return {
                "message": f"Đã xử lý toàn bộ {total_processed} bản ghi từ crawl_db!"
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Lỗi khi xử lý: {str(e)}")
    
    return router