from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from config import CHROMEDRIVER_PATH, PROFILE_PATH, SUSPICIOUS_URLS, TRUSTED_URLS
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def crawl_facebook_page(url: str, target_posts: int) -> list:
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-data-dir={PROFILE_PATH}")
    options.add_argument("--profile-directory=Default")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")

    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        logger.info("Đang mở Facebook...")
        driver.get("https://www.facebook.com/")
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        logger.info(f"Truy cập trang: {url}")
        driver.get(url)
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(3)

        posts = []
        seen_texts = set()
        scroll_attempts = 0
        max_scroll_attempts = 30

        # Chuẩn hóa URL để so sánh
        normalized_url = url.lower().replace('http://', '').replace('https://', '').replace('www.', '')
        is_suspicious = any(suspicious_url.replace('http://', '').replace('https://', '').replace('www.', '') in normalized_url 
                           for suspicious_url in SUSPICIOUS_URLS)
        is_trusted = any(trusted_url.replace('http://', '').replace('https://', '').replace('www.', '') in normalized_url 
                        for trusted_url in TRUSTED_URLS)

        logger.info(f"URL: {url}, is_suspicious: {is_suspicious}, is_trusted: {is_trusted}")

        while len(posts) < target_posts and scroll_attempts < max_scroll_attempts:
            scroll_attempts += 1
            logger.info(f"Cuộn lần thứ {scroll_attempts}...")

            see_more_buttons = driver.find_elements(By.XPATH, '//div[@role="button" and (text()="Xem thêm" or contains(text(),"See more"))]')
            for button in see_more_buttons:
                try:
                    driver.execute_script("arguments[0].click();", button)
                except Exception:
                    continue

            post_elements = driver.find_elements(By.XPATH, 
                '//div[contains(@data-ad-comet-preview,"message")] | '
                '//div[contains(@class,"x1vvkbs") and string-length(normalize-space(text())) > 0]'
            )

            for post_element in post_elements:
                try:
                    text = post_element.text.strip()
                    if text and text not in seen_texts:
                        seen_texts.add(text)
                        posts.append({"text": text, "is_suspicious": is_suspicious, "is_trusted": is_trusted})
                        logger.info(f"Đã lấy {len(posts)} bài viết")
                        if len(posts) >= target_posts:
                            break
                except Exception:
                    continue

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

        if len(posts) < target_posts:
            logger.info(f"Chỉ lấy được {len(posts)} bài viết sau {scroll_attempts} lần cuộn.")

        return posts[:target_posts]

    finally:
        logger.info("Đóng trình duyệt...")
        driver.quit()