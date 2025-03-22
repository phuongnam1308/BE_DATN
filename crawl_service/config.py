from dotenv import load_dotenv
import os

load_dotenv()

# Hàm kiểm tra biến môi trường
def get_env_var(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise ValueError(f"Biến môi trường {name} không được định nghĩa trong .env")
    return value

# Cấu hình cơ sở dữ liệu
DB_CONFIG = {
    "host": get_env_var("DB_HOST"),
    "port": get_env_var("DB_PORT"),
    "database": get_env_var("DB_NAME"),
    "user": get_env_var("DB_USER"),
    "password": get_env_var("DB_PASSWORD")
}

# Cấu hình Selenium
CHROMEDRIVER_PATH = get_env_var("CHROMEDRIVER_PATH")
PROFILE_PATH = get_env_var("PROFILE_PATH")
TARGET_POSTS = int(get_env_var("TARGET_POSTS"))

# Cấu hình dịch vụ
CRAWL_SERVICE_PORT = int(get_env_var("CRAWL_SERVICE_PORT"))