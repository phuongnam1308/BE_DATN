from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
from config import CHROMEDRIVER_PATH, PROFILE_PATH

def crawl_facebook_page(url: str, target_posts: int) -> list:
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-data-dir={PROFILE_PATH}")
    options.add_argument("--profile-directory=Default")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")

    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get("https://www.facebook.com/")
        time.sleep(5)

        driver.get(url)
        time.sleep(5)

        last_height = driver.execute_script("return document.body.scrollHeight")
        posts = set()

        while len(posts) < target_posts:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

            see_more_buttons = driver.find_elements(By.XPATH, '//div[@role="button" and contains(text(),"Xem thêm")]')
            for button in see_more_buttons:
                try:
                    driver.execute_script("arguments[0].click();", button)
                    time.sleep(1)
                except:
                    continue

            post_elements = driver.find_elements(By.CSS_SELECTOR, 'div[dir="auto"][style*="text-align"]')
            for post in post_elements:
                text = post.text.strip()
                if len(text) > 30 and text not in posts:
                    posts.add(text)

            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        return list(posts)[:target_posts]

    finally:
        driver.quit()