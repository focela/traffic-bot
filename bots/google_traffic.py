import sys
import os
import time
import random

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Ensure the correct system path is set for module resolution
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.proxy_manager import get_valid_smartproxy
from utils.user_agent_manager import get_random_user_agent
from utils.logger import log_message


def configure_webdriver():
    """
    Configure the Selenium WebDriver with proxy and user-agent settings.

    Returns:
        webdriver.Chrome: Configured Chrome WebDriver instance.
    """
    proxy = get_valid_smartproxy()
    user_agent = get_random_user_agent()

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument(f"user-agent={user_agent}")

    if proxy:
        options.add_argument(f"--proxy-server={proxy}")

    return webdriver.Chrome(options=options)


def load_keywords():
    """
    Load search keywords from the project's config/keywords.txt file.

    Returns:
        list: A list of keywords.
    """
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    keywords_file = os.path.join(base_path, "config/keywords.txt")
    try:
        with open(keywords_file, "r", encoding="utf-8") as file:
            keywords = [line.strip() for line in file.readlines() if line.strip()]
        return keywords
    except Exception as e:
        log_message(f"⚠️ Could not load keywords file: {e}", "error")
        return ["site:trants.me"]  # Default keyword if file read fails


def search_google(driver):
    """
    Search Google for the target website using keywords from the config file.

    Args:
        driver (webdriver.Chrome): Selenium WebDriver instance.

    Returns:
        bool: True if the website was found and clicked, False otherwise.
    """
    keywords = load_keywords()
    search_query = random.choice(keywords)
    log_message(f"🔍 Using search keyword: {search_query}")

    driver.get("https://www.google.com")
    time.sleep(random.uniform(2, 4))

    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(search_query)
    search_box.send_keys(Keys.RETURN)
    time.sleep(random.uniform(4, 6))

    links = driver.find_elements(By.CSS_SELECTOR, "h3")
    for link in links:
        parent = link.find_element(By.XPATH, "./..")
        if "trants.me" in parent.get_attribute("href"):
            log_message(f"✅ Found website on Google: {parent.get_attribute('href')}")
            parent.click()
            return True

    log_message("⚠️ Not found on Google. Redirecting to homepage trants.me...")
    driver.get("https://trants.me")
    time.sleep(random.uniform(5, 10))
    return True


def browse_random_article(driver):
    """
    Click on a random article link on the target website and simulate scrolling.

    Args:
        driver (webdriver.Chrome): Selenium WebDriver instance.
    """
    article_links = driver.find_elements(By.CSS_SELECTOR, "a")
    valid_links = [a for a in article_links if "trants.me" in a.get_attribute("href") and not a.find_elements(By.XPATH,
                                                                                                              "ancestor::div[contains(@class, 'image')]")]

    if valid_links:
        article = random.choice(valid_links)
        log_message(f"🔗 Clicking on article: {article.get_attribute('href')}")

        # Simulate scrolling to create a more human-like behavior
        for _ in range(random.randint(3, 6)):
            scroll_distance = random.randint(300, 1000)
            driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
            time.sleep(random.uniform(3, 6))


def main():
    """
    Main function to execute the bot logic, handling errors and ensuring WebDriver cleanup.
    """
    driver = configure_webdriver()
    try:
        if search_google(driver):
            browse_random_article(driver)
        log_message("🚀 Traffic generated successfully!")
    except Exception as e:
        log_message(f"❌ Error running bot: {e}", "error")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
