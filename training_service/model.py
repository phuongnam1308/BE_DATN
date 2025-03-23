import torch
import torch.nn as nn
import numpy as np

# Định nghĩa mô hình ConvNet
class ConvNet(nn.Module):
    def __init__(self, input_size, output_size, dropout_rate=0.2):
        super(ConvNet, self).__init__()
        self.fc1 = nn.Linear(input_size, 1024)
        self.dropout1 = nn.Dropout(dropout_rate)
        self.fc2 = nn.Linear(1024, 256)
        self.dropout2 = nn.Dropout(dropout_rate)
        self.fc3 = nn.Linear(256, 64)
        self.dropout3 = nn.Dropout(dropout_rate)
        self.fc4 = nn.Linear(64, output_size)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.dropout1(x)
        x = self.relu(self.fc2(x))
        x = self.dropout2(x)
        x = self.relu(self.fc3(x))
        x = self.dropout3(x)
        logits = self.fc4(x)
        probs = torch.softmax(logits, dim=1)
        return logits, probs

# Trích xuất đặc trưng từ PhoBERT theo batch
def extract_text_features_batch(texts, device, phobert_model, tokenizer):
    encoded_input = tokenizer(texts, padding=True, truncation=True, return_tensors='pt', max_length=256).to(device)
    with torch.no_grad():
        model_output = phobert_model(**encoded_input)
    return model_output.last_hidden_state[:, 0, :].cpu().numpy()

# Dự đoán nhãn theo batch
def predict_news_type_batch(texts, model, device, phobert_model, tokenizer):
    features = extract_text_features_batch(texts, device, phobert_model, tokenizer)
    features_tensor = torch.tensor(features, dtype=torch.float32).to(device)
    
    model.eval()
    with torch.no_grad():
        logits, probs = model(features_tensor)
        _, predicted = torch.max(logits, 1)
    
    predictions = predicted.cpu().numpy()
    probabilities = probs.cpu().numpy()
    label_mapping = {
        0: "Tin thường",
        1: "Tin giả về đời sống xã hội",
        2: "Tin giả về chính trị"
    }
    predicted_labels = [label_mapping[p] for p in predictions]
    
    return predicted_labels, probabilities