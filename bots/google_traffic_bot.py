from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from proxy_manager.proxy_handler import get_proxy, create_proxy_extension
from utils.logger import log_message

proxy = get_proxy("google_bot")
proxy_extension = create_proxy_extension(proxy)

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Load the proxy authentication extension
chrome_options.add_extension(proxy_extension)

# Use WebDriverManager for automatic ChromeDriver updates
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)


def run():
    log_message("google_traffic_bot", f"Starting bot with proxy: {proxy}")
    driver.get("https://www.google.com/")

    try:
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        search_box.send_keys("AWS automation using Selenium")
        search_box.submit()
        log_message("google_traffic_bot", "Search executed successfully")
    except Exception as e:
        log_message("google_traffic_bot", f"Error: {str(e)}")
    finally:
        time.sleep(5)
        driver.quit()


if __name__ == "__main__":
    run()
