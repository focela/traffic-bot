import sys
import os
import time
import random
import traceback

# Ensure the correct system path is set for module resolution
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException, TimeoutException, ElementNotInteractableException,
    WebDriverException, StaleElementReferenceException
)

from utils.proxy_manager import get_valid_smartproxy
from utils.user_agent_manager import get_random_user_agent
from utils.logger import log_message


def configure_webdriver():
    """
    Configure and initialize the Selenium WebDriver with proxy and user-agent settings.

    Returns:
        webdriver.Chrome: Configured WebDriver instance.
    """
    proxy = get_valid_smartproxy()
    user_agent = get_random_user_agent()

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument(f"user-agent={user_agent}")

    if proxy:
        options.add_argument(f"--proxy-server={proxy}")

    return webdriver.Chrome(options=options)


def perform_google_search(driver):
    """
    Perform a Google search for the target website and attempt to click on its link.

    Args:
        driver (webdriver.Chrome): Selenium WebDriver instance.

    Returns:
        bool: True if the website link was found and clicked, otherwise False.
    """
    driver.get("https://www.google.com")
    time.sleep(random.uniform(2, 4))

    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys("site:trants.me")
    search_box.send_keys(Keys.RETURN)
    time.sleep(random.uniform(4, 6))

    links = driver.find_elements(By.CSS_SELECTOR, "h3")
    for link in links:
        try:
            parent = link.find_element(By.XPATH, "./..")
            if "trants.me" in parent.get_attribute("href"):
                log_message(f"✅ Found website on Google: {parent.get_attribute('href')}")
                parent.click()
                return True
        except NoSuchElementException:
            log_message("⚠️ No valid link found in search results!", "warning")

    return False


def browse_random_article(driver):
    """
    Click on a random article link from the website and scroll through the page.

    Args:
        driver (webdriver.Chrome): Selenium WebDriver instance.
    """
    for _ in range(3):  # Retry up to 3 times in case of stale elements
        try:
            article_links = driver.find_elements(By.CSS_SELECTOR, "a")
            valid_links = [a for a in article_links if "trants.me" in a.get_attribute("href")]

            if valid_links:
                article = random.choice(valid_links)
                driver.execute_script("arguments[0].click();", article)
                log_message(f"🔗 Clicking on article: {article.get_attribute('href')}")
                time.sleep(random.uniform(5, 15))
                break
        except StaleElementReferenceException:
            log_message("⚠️ Stale element error, retrying...", "warning")
            time.sleep(2)

    # Random scrolling simulation
    for _ in range(random.randint(3, 6)):
        scroll_distance = random.randint(300, 1000)
        driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
        time.sleep(random.uniform(3, 6))


def main():
    """
    Main function to execute the automated AdSense click bot.
    """
    driver = configure_webdriver()
    try:
        found = perform_google_search(driver)
        if not found:
            log_message("⚠️ Website not found on Google, redirecting to homepage...")
            driver.get("https://trants.me")
            time.sleep(random.uniform(5, 10))

        browse_random_article(driver)
        log_message("🚀 Traffic successfully generated!")

    except (
    NoSuchElementException, TimeoutException, ElementNotInteractableException, StaleElementReferenceException) as e:
        log_message(f"⚠️ Web interaction error: {e}", "warning")
    except WebDriverException as e:
        log_message(f"❌ WebDriver error: {e}", "error")
    except Exception as e:
        log_message(f"❌ Unexpected error: {e}", "error")
        log_message(traceback.format_exc(), "error")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
