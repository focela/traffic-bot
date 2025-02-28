"""
Google Traffic Bot - Simulates human-like traffic to websites via Google search.

This module provides a bot that searches for target websites on Google and visits them,
either through search results or directly. It simulates human behavior to avoid detection.
"""

import logging
import os
import random
import time
from typing import Optional, Dict, Any

from selenium import webdriver
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementNotInteractableException
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from proxy_manager.proxy_handler import get_proxy, create_proxy_extension
from utils.logger import log_message

# Configure logging
logger = logging.getLogger(__name__)


class GoogleTrafficBot:
    """Bot that simulates human-like traffic to websites via Google search."""

    # Default configuration
    DEFAULT_CONFIG = {
        "target_website": "https://trants.me",
        "search_keyword": "AWS automation site:trants.me",
        "bot_name": "google_bot",
        "headless": True,
        "user_agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/96.0.4664.110 Safari/537.36"
        ),
        "viewport_width": 1920,
        "viewport_height": 1080
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Google Traffic Bot with configuration.

        Args:
            config: Optional dictionary with configuration overrides
        """
        # Merge default config with provided config
        self.config = self.DEFAULT_CONFIG.copy()
        if config:
            self.config.update(config)

        self.driver = None
        self.proxy = None
        self.proxy_extension_path = None

    def setup_driver(self) -> None:
        """
        Set up the Chrome WebDriver with appropriate options and proxy configuration.
        """
        log_message("google_traffic_bot", "Setting up Chrome WebDriver...")

        # Get proxy and create authentication extension
        self.proxy = get_proxy(self.config["bot_name"])
        self.proxy_extension_path = create_proxy_extension(self.proxy)

        # Configure Chrome options
        chrome_options = Options()

        # Set headless mode based on configuration
        if self.config["headless"]:
            chrome_options.add_argument("--headless")

        # Set up window size and user agent to mimic real browser
        chrome_options.add_argument(f"--window-size={self.config['viewport_width']},{self.config['viewport_height']}")
        chrome_options.add_argument(f"user-agent={self.config['user_agent']}")

        # Add necessary Chrome options for stable operation
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")

        # Add language settings to appear more natural
        chrome_options.add_argument("--lang=en-US,en;q=0.9")

        # Add proxy extension
        chrome_options.add_extension(self.proxy_extension_path)

        # Disable automation flags to avoid detection
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)

        # Use WebDriverManager to manage ChromeDriver updates
        service = Service(ChromeDriverManager().install())

        # Initialize the Chrome WebDriver
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

        # Execute CDP commands to prevent detection
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """
        })

        log_message("google_traffic_bot", f"WebDriver set up with proxy: {self.proxy}")

    def simulate_human_behavior(self) -> None:
        """
        Simulate human-like behavior during browsing to avoid detection.
        """
        # Randomize scroll behavior
        scroll_amount = random.randint(300, 700)
        self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        time.sleep(random.uniform(0.5, 2.0))

        # Sometimes scroll back up
        if random.random() < 0.3:
            self.driver.execute_script(f"window.scrollBy(0, -{random.randint(100, 300)});")
            time.sleep(random.uniform(0.5, 1.5))

        # Random mouse movements (simulated via JavaScript)
        if random.random() < 0.4:
            x = random.randint(100, 800)
            y = random.randint(100, 600)
            self.driver.execute_script(
                f"document.elementFromPoint({x}, {y}).dispatchEvent(new MouseEvent('mouseover'));")
            time.sleep(random.uniform(0.3, 1.0))

    def search_google(self) -> bool:
        """
        Search Google for the target website and click if found.

        Returns:
            True if target website was found and clicked, False otherwise
        """
        log_message("google_traffic_bot", f"Searching Google for: '{self.config['search_keyword']}'")

        try:
            # Navigate to Google
            self.driver.get("https://www.google.com/")
            time.sleep(random.uniform(1, 3))  # Delay to mimic human behavior

            # Accept cookies if the dialog appears
            try:
                cookie_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Accept all')]"))
                )
                cookie_button.click()
                time.sleep(random.uniform(0.5, 1.5))
            except (TimeoutException, NoSuchElementException):
                # Cookie dialog might not appear, which is fine
                pass

            # Find search box and enter the search keyword
            search_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "q"))
            )

            # Type slowly like a human would
            for char in self.config["search_keyword"]:
                search_box.send_keys(char)
                time.sleep(random.uniform(0.05, 0.2))

            # Sometimes pause briefly while typing
            if random.random() < 0.3:
                time.sleep(random.uniform(0.5, 1.5))

            # Submit the search
            search_box.send_keys(Keys.RETURN)
            log_message("google_traffic_bot", "Search executed successfully")

            # Wait for results to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.g"))
            )

            # Simulate human reading the results
            time.sleep(random.uniform(1, 3))
            self.simulate_human_behavior()

            # Check if target website appears in the search results
            results = self.driver.find_elements(By.CSS_SELECTOR, "div.tF2Cxc a, div.yuRUbf a")

            for result in results:
                link = result.get_attribute("href")
                log_message("google_traffic_bot", f"Checking result: {link}")

                if self.config["target_website"] in link:
                    log_message("google_traffic_bot", f"Website FOUND in Google results: {link}")

                    # Scroll to the element before clicking
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", result)
                    time.sleep(random.uniform(0.5, 1.5))

                    # Click the result
                    result.click()

                    # Simulate reading time
                    self._simulate_reading()
                    return True

            log_message("google_traffic_bot", f"Website NOT found in search results.")
            return False

        except Exception as e:
            log_message("google_traffic_bot", f"Error during Google search: {str(e)}")
            return False

    def visit_website_directly(self) -> None:
        """
        Visit the target website directly and interact with a random article.
        """
        log_message("google_traffic_bot", f"Visiting {self.config['target_website']} directly.")

        try:
            # Navigate to the target website
            self.driver.get(self.config["target_website"])

            # Wait for the page to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Simulate initial page browsing
            time.sleep(random.uniform(2, 5))
            self.simulate_human_behavior()

            # Find article links
            selectors = [
                "div.post-item .image a",
                "article .entry-title a",
                ".blog-post a.read-more",
                ".article-title a"
            ]

            articles = []
            for selector in selectors:
                found_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if found_elements:
                    articles.extend(found_elements)

            if articles:
                # Shuffle to randomize article selection
                random.shuffle(articles)

                for article in articles[:5]:  # Try at most 5 articles
                    try:
                        article_url = article.get_attribute("href")

                        if not article_url or "#" in article_url or "javascript:" in article_url:
                            continue  # Skip empty or invalid links

                        # Scroll to make the element visible
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", article)
                        time.sleep(random.uniform(1, 2))

                        # Click the article
                        WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(article))
                        article.click()
                        log_message("google_traffic_bot", f"Clicked on article: {article_url}")

                        # Simulate reading the article
                        self._simulate_reading()
                        return

                    except (ElementNotInteractableException, TimeoutException) as e:
                        log_message("google_traffic_bot", f"Skipping article due to error: {str(e)}")
                        continue  # Try the next article

            log_message("google_traffic_bot", "No valid articles found to click.")

        except Exception as e:
            log_message("google_traffic_bot", f"Error while visiting website directly: {str(e)}")

    def _simulate_reading(self) -> None:
        """
        Simulate human reading behavior on a page.
        """
        # Determine reading time based on content length
        try:
            content_elements = self.driver.find_elements(By.CSS_SELECTOR, "p, h1, h2, h3, article, .content")
            content_length = sum(len(elem.text) for elem in content_elements if elem.text)

            # Adjust reading time based on content length
            base_time = random.uniform(5, 10)
            reading_time = min(base_time + (content_length / 1000), 30)  # Cap at 30 seconds
        except Exception:
            # Default reading time if content analysis fails
            reading_time = random.uniform(10, 20)

        # Scroll through the content gradually
        scroll_interval = reading_time / 5  # Divide reading time into scrolling intervals

        for _ in range(5):
            self.simulate_human_behavior()
            time.sleep(scroll_interval)

        # Sometimes click on internal links
        if random.random() < 0.3:
            try:
                internal_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href^='/']")
                if internal_links:
                    link = random.choice(internal_links)
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link)
                    time.sleep(random.uniform(0.5, 1.5))
                    link.click()
                    time.sleep(random.uniform(3, 7))
            except Exception:
                pass

    def run(self) -> None:
        """
        Run the Google Traffic Bot workflow.
        """
        log_message("google_traffic_bot", "Starting Google Traffic Bot...")

        try:
            # Set up the WebDriver
            self.setup_driver()

            # Search Google for the target website
            found = self.search_google()

            # Visit directly if not found via search
            if not found:
                self.visit_website_directly()

            log_message("google_traffic_bot", "Bot session completed successfully.")

        except Exception as e:
            log_message("google_traffic_bot", f"Error during bot execution: {str(e)}")

        finally:
            # Clean up
            if self.driver:
                self.driver.quit()

            # Remove temporary proxy extension file if it exists
            if self.proxy_extension_path and os.path.exists(self.proxy_extension_path):
                try:
                    os.remove(self.proxy_extension_path)
                except Exception:
                    pass


def run(config: Optional[Dict[str, Any]] = None) -> None:
    """
    Run the Google Traffic Bot with optional configuration.

    Args:
        config: Optional dictionary containing configuration parameters
    """
    bot = GoogleTrafficBot(config)
    bot.run()


if __name__ == "__main__":
    run()
