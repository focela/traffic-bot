import sys
import os
import time
import random

# Ensure the correct system path is set for module resolution
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from utils.proxy_manager import get_valid_smartproxy
from utils.user_agent_manager import get_random_user_agent
from utils.logger import log_message


def load_referral_links():
    """
    Load the list of referral links from the configuration file.

    Returns:
        list: A list of referral links or an empty list if the file is missing or empty.
    """
    try:
        with open("config/referral_links.txt", "r") as f:
            links = [line.strip() for line in f.readlines() if line.strip()]
        if not links:
            log_message("❌ No referral links found in the file!", "error")
        return links
    except FileNotFoundError:
        log_message("❌ Referral links configuration file not found!", "error")
        return []


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


def simulate_social_traffic(driver, referral_links):
    """
    Simulate user visiting and interacting with a referral link.

    Args:
        driver (webdriver.Chrome): Selenium WebDriver instance.
        referral_links (list): List of referral links.
    """
    referral_url = random.choice(referral_links)
    log_message(f"🚀 Visiting social referral link: {referral_url}")
    driver.get(referral_url)
    time.sleep(5)

    links = driver.find_elements(By.CSS_SELECTOR, "a")
    clicked = False
    for link in links:
        href = link.get_attribute("href")
        if href and "trants.me" in href:
            log_message(f"🔗 Clicking on link: {href}")
            try:
                driver.execute_script("arguments[0].scrollIntoView();", link)
                time.sleep(1)
                ActionChains(driver).move_to_element(link).click().perform()
                clicked = True
                break
            except Exception as e:
                log_message(f"⚠️ Click intercepted, trying alternative method: {e}", "warning")
                driver.execute_script("arguments[0].click();", link)
                clicked = True
                break

    if not clicked:
        log_message("⚠️ No valid articles found to click!", "warning")

    time.sleep(random.randint(10, 30))
    log_message("✅ Successfully generated social media traffic!")


def main():
    """
    Main function to execute the referral traffic bot logic.
    """
    referral_links = load_referral_links()
    if not referral_links:
        log_message("⚠️ No referral links available to run the bot!", "warning")
        sys.exit(1)

    driver = configure_webdriver()
    try:
        simulate_social_traffic(driver, referral_links)
    except Exception as e:
        log_message(f"❌ Error running bot: {e}", "error")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
