import time
import sys
import os
# Ensure the correct system path is set for module resolution
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from proxy_manager.proxy_handler import get_proxy
from utils.logger import log_message

proxy = get_proxy("google_bot")

options = Options()
options.add_argument(f'--proxy-server={proxy}')
options.add_argument("--headless")

driver = webdriver.Chrome(options=options)

def run():
    log_message("google_traffic_bot", "Starting bot...")
    driver.get("https://www.google.com/")
    time.sleep(3)
    search_box = driver.find_element("name", "q")
    search_box.send_keys("AWS automation using Selenium")
    search_box.submit()
    time.sleep(5)
    results = driver.find_elements("css selector", "h3")
    if results:
        results[0].click()
        log_message("google_traffic_bot", "Clicked search result")
        time.sleep(10)
    driver.quit()

if __name__ == "__main__":
    run()
