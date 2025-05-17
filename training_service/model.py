import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer
import logging
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_phobert_and_tokenizer(model_name):
    try:
        phobert_model = AutoModel.from_pretrained(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        logger.info(f"Đã tải PhoBERT model và tokenizer từ {model_name}")
        return phobert_model, tokenizer
    except Exception as e:
        logger.error(f"Lỗi khi tải PhoBERT model hoặc tokenizer: {str(e)}")
        raise

class ConvNet(nn.Module):
    def __init__(self, num_classes=3):
        super(ConvNet, self).__init__()
        self.fc1 = nn.Linear(768, 1024)
        self.fc2 = nn.Linear(1024, 256)
        self.fc3 = nn.Linear(256, 64)
        self.fc4 = nn.Linear(64, num_classes)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.5)

    def forward(self, x):
        x = x.mean(dim=1)  # Pooling: lấy trung bình theo chiều sequence
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.relu(self.fc3(x))
        x = self.dropout(x)
        x = self.fc4(x)
        return x

def predict_news_type_batch(texts, model, device, phobert_model, tokenizer, is_suspicious_list=None, is_trusted_list=None):
    try:
        model.eval()
        phobert_model.eval()
        encoded_input = tokenizer(texts, padding=True, truncation=True, return_tensors='pt', max_length=256).to(device)
        
        with torch.no_grad():
            outputs = phobert_model(**encoded_input)
            embeddings = outputs.last_hidden_state
            logits = model(embeddings)
            probabilities = torch.softmax(logits, dim=1)
            probabilities = probabilities.cpu().numpy()

        # Ghi log giá trị is_suspicious và is_trusted
        logger.info(f"is_suspicious_list: {is_suspicious_list}")
        logger.info(f"is_trusted_list: {is_trusted_list}")
        logger.info(f"Xác suất ban đầu: {probabilities.tolist()}")

        # Điều chỉnh xác suất dựa trên is_suspicious và is_trusted
        for i in range(len(texts)):
            if is_suspicious_list and is_suspicious_list[i]:
                # Cộng 60% vào xác suất nhãn "Tin giả về chính trị" (index 2)
                probabilities[i][2] = min(probabilities[i][2] + 0.6, 1.0)
                remaining_prob = 1.0 - probabilities[i][2]
                total_other = probabilities[i][0] + probabilities[i][1]
                if total_other > 0:
                    scale = remaining_prob / total_other
                    probabilities[i][0] *= scale
                    probabilities[i][1] *= scale
                else:
                    probabilities[i][0] = remaining_prob / 2
                    probabilities[i][1] = remaining_prob / 2
                logger.info(f"Bài viết {i} (suspicious): Xác suất sau điều chỉnh: {probabilities[i].tolist()}")
            elif is_trusted_list and is_trusted_list[i]:
                # Cộng 50% vào xác suất nhãn "Tin thường" (index 0)
                probabilities[i][0] = min(probabilities[i][0] + 0.5, 1.0)
                remaining_prob = 1.0 - probabilities[i][0]
                total_other = probabilities[i][1] + probabilities[i][2]
                if total_other > 0:
                    scale = remaining_prob / total_other
                    probabilities[i][1] *= scale
                    probabilities[i][2] *= scale
                else:
                    probabilities[i][1] = remaining_prob / 2
                    probabilities[i][2] = remaining_prob / 2
                logger.info(f"Bài viết {i} (trusted): Xác suất sau điều chỉnh: {probabilities[i].tolist()}")

        predicted_indices = np.argmax(probabilities, axis=1)
        label_map = {0: "Tin thường", 1: "Tin giả về đời sống xã hội", 2: "Tin giả về chính trị"}
        predicted_labels = [label_map[idx] for idx in predicted_indices]
        
        logger.info(f"Dự đoán hoàn tất cho {len(texts)} bài viết")
        logger.info(f"Xác suất cuối cùng: {probabilities.tolist()}")
        return predicted_labels, probabilities
    except Exception as e:
        logger.error(f"Lỗi khi dự đoán: {str(e)}")
        raise