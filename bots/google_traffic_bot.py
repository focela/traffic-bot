"""
Google Traffic Bot with optimized keyword configuration.
"""

import os
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from proxy_manager.proxy_handler import get_proxy, create_proxy_extension
from utils.logger import log_message

# Import config module
from utils.config import load_config, generate_search_keyword

# Xác định đường dẫn đến file cấu hình
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
config_path = os.path.join(project_root, 'configs', 'environment.json')

# Load configuration
config = load_config(config_path)

# Set target website from config
TARGET_WEBSITE = config['target_website']

# Get bot name (cố định)
BOT_NAME = "google_bot"

# Get proxy and create authentication extension
proxy = get_proxy(BOT_NAME)
proxy_extension = create_proxy_extension(proxy)

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_extension(proxy_extension)

# Use WebDriverManager to manage ChromeDriver updates
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)


def search_google():
    """Search Google for the target website and return if found."""
    # Tạo từ khóa tìm kiếm bằng cách kết hợp một từ khóa ngẫu nhiên với site filter
    # (hàm generate_search_keyword đã được gọi trong load_config)
    search_keyword = config['search_keyword']

    log_message("google_traffic_bot", f"Starting bot with proxy: {proxy}")
    log_message("google_traffic_bot", f"Searching Google for: '{search_keyword}'")
    log_message("google_traffic_bot", f"Target website: {TARGET_WEBSITE}")

    driver.get("https://www.google.com/")

    try:
        # Find search box and enter the search keyword
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        search_box.send_keys(search_keyword)
        search_box.submit()
        log_message("google_traffic_bot", "Search executed successfully")

        # Wait for results to load
        time.sleep(3)

        # Check if target website appears in the search results
        results = driver.find_elements(By.CSS_SELECTOR, "div.tF2Cxc a")
        for result in results:
            link = result.get_attribute("href")
            log_message("google_traffic_bot", f"Checking result: {link}")
            if TARGET_WEBSITE in link:
                log_message("google_traffic_bot", f"Website FOUND in Google results: {link}")
                result.click()
                time.sleep(random.uniform(10, 20))  # Simulate reading time
                return True

        log_message("google_traffic_bot", f"Website NOT found in search results.")
        return False

    except Exception as e:
        log_message("google_traffic_bot", f"Error during Google search: {str(e)}")
        return False


def visit_website_directly():
    """If the website is not found on Google, visit it directly and click a random article."""
    log_message("google_traffic_bot", f"Visiting {TARGET_WEBSITE} directly.")
    driver.get(TARGET_WEBSITE)
    time.sleep(random.uniform(5, 10))  # Simulate reading time

    try:
        # Find article links inside post-item (avoiding user profiles)
        articles = driver.find_elements(By.CSS_SELECTOR, "div.post-item .image a")

        if articles:
            random.shuffle(articles)  # Randomize article selection
            for article in articles:
                try:
                    article_url = article.get_attribute("href")

                    if not article_url or "#" in article_url:
                        continue  # Skip empty or invalid links

                    # Ensure the element is visible before clicking
                    driver.execute_script("arguments[0].scrollIntoView();", article)
                    WebDriverWait(driver, 5).until(EC.element_to_be_clickable(article))
                    article.click()
                    log_message("google_traffic_bot", f"Clicked on article: {article_url}")
                    time.sleep(random.uniform(10, 20))  # Simulate reading time
                    return  # Exit function after a successful click
                except Exception as e:
                    log_message("google_traffic_bot", f"Skipping article due to error: {str(e)}")
                    continue  # Try the next article

        log_message("google_traffic_bot", "No valid articles found to click.")

    except Exception as e:
        log_message("google_traffic_bot", f"Error while visiting website directly: {str(e)}")


def run():
    found = search_google()
    if not found:
        visit_website_directly()

    log_message("google_traffic_bot", "Bot session completed.")
    driver.quit()


if __name__ == "__main__":
    run()
