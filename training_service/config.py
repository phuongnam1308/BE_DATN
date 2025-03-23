from dotenv import load_dotenv
import os

load_dotenv()

def get_env_var(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise ValueError(f"Biến môi trường {name} không được định nghĩa trong .env")
    return value

CRAWL_DB_CONFIG = {
    "host": get_env_var("CRAWL_DB_HOST"),
    "port": get_env_var("CRAWL_DB_PORT"),
    "database": get_env_var("CRAWL_DB_NAME"),
    "user": get_env_var("CRAWL_DB_USER"),
    "password": get_env_var("CRAWL_DB_PASSWORD")
}

TRAINING_DB_CONFIG = {
    "host": get_env_var("TRAINING_DB_HOST"),
    "port": get_env_var("TRAINING_DB_PORT"),
    "database": get_env_var("TRAINING_DB_NAME"),
    "user": get_env_var("TRAINING_DB_USER"),
    "password": get_env_var("TRAINING_DB_PASSWORD")
}

TRAINING_SERVICE_PORT = int(get_env_var("TRAINING_SERVICE_PORT"))
MODEL_PATH = get_env_var("MODEL_PATH")
PHOBERT_MODEL_NAME = "vinai/phobert-base"
NUM_CLASSES = 3