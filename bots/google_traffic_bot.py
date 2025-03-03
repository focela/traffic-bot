"""
Google Traffic Bot - Simulates human-like traffic to websites via Google search.

This module provides a bot that searches for target websites on Google and visits them,
with support for dynamic proxy selection and search keyword customization.
"""

import os
import time
import random
from typing import Dict, Any, Optional

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementNotInteractableException,
    WebDriverException
)
from webdriver_manager.chrome import ChromeDriverManager

from proxy_manager.proxy_handler import get_proxy, create_proxy_extension
from utils.logger import log_message
from utils.config import load_config


def get_random_user_agent():
    """
    Get a random user agent to increase diversity.

    Returns:
        Random user agent string
    """
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 OPR/82.0.4227.44"
    ]
    return random.choice(user_agents)


def search_google(driver, search_keyword, target_website, bot_id="unknown"):
    """
    Search Google for the target website and return if found.

    Args:
        driver: WebDriver instance
        search_keyword: Keyword to search for
        target_website: Target website to look for in results
        bot_id: Identifier for this bot instance

    Returns:
        True if target website was found and clicked, False otherwise
    """
    log_message(f"google_bot_{bot_id}", f"Searching Google for: '{search_keyword}'")
    log_message(f"google_bot_{bot_id}", f"Target website: {target_website}")

    try:
        # Navigate to Google with randomized entry point
        google_domains = ["https://www.google.com/", "https://www.google.co.uk/", "https://www.google.com.sg/"]
        driver.get(random.choice(google_domains))

        # Add some random delay to appear more human-like
        time.sleep(random.uniform(1, 3))

        # Accept cookies if the dialog appears
        try:
            cookie_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Accept all')]"))
            )
            cookie_button.click()
            time.sleep(random.uniform(0.5, 1.5))
        except (TimeoutException, NoSuchElementException):
            # Cookie dialog might not appear, which is fine
            pass

        # Find search box and enter the search keyword
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "q"))
        )

        # Type slowly like a human would
        for char in search_keyword:
            search_box.send_keys(char)
            time.sleep(random.uniform(0.05, 0.2))

        # Random pauses while typing
        if random.random() < 0.3:
            time.sleep(random.uniform(0.5, 1.2))

        # Submit the search
        search_box.send_keys(Keys.RETURN)
        log_message(f"google_bot_{bot_id}", "Search executed successfully")

        # Wait for results to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.g"))
        )

        # Random delay to simulate reading results
        time.sleep(random.uniform(2, 5))

        # Scroll down slightly
        driver.execute_script("window.scrollBy(0, 300);")
        time.sleep(random.uniform(1, 2))

        # Check if target website appears in the search results
        result_selectors = [
            "div.tF2Cxc a",
            "div.yuRUbf a",
            "div.g div.yuRUbf a"
        ]

        results = []
        for selector in result_selectors:
            found_elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if found_elements:
                results.extend(found_elements)

        for result in results:
            link = result.get_attribute("href")
            log_message(f"google_bot_{bot_id}", f"Checking result: {link}")

            if target_website in link:
                log_message(f"google_bot_{bot_id}", f"Website FOUND in Google results: {link}")

                # Scroll to make element visible
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", result)
                time.sleep(random.uniform(0.5, 1.5))

                # Click the result
                result.click()

                # Simulate reading time
                simulate_human_reading(driver, bot_id)
                return True

        log_message(f"google_bot_{bot_id}", f"Website NOT found in search results.")
        return False

    except Exception as e:
        log_message(f"google_bot_{bot_id}", f"Error during Google search: {str(e)}", level="ERROR")
        return False


def visit_website_directly(driver, target_website, bot_id="unknown"):
    """
    Visit the target website directly and interact with a random article.
    First attempts to load more articles by clicking "load more" button if available.

    Args:
        driver: WebDriver instance
        target_website: Website to visit directly
        bot_id: Identifier for this bot instance
    """
    log_message(f"google_bot_{bot_id}", f"Visiting {target_website} directly.")

    try:
        # Navigate to the target website
        driver.get(target_website)

        # Wait for the page to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # Random initial delay to simulate page loading observation
        time.sleep(random.uniform(2, 5))

        # Scroll down slightly
        driver.execute_script(f"window.scrollBy(0, {random.randint(300, 700)});")
        time.sleep(random.uniform(1, 3))

        # Try to find and click on "load more" button to see more articles
        # Using multiple possible selectors for "load more" buttons
        load_more_selectors = [
            "a.btn-load-more",
            "button.load-more",
            ".load-more a",
            ".load-more button",
            "a.view-more",
            "button.view-more",
            ".pagination a",
            ".pagination-next a",
            "a.next-posts",
            "a.next",
            "a[href*='page']",
            "button[data-load-more]",
            ".btn-load-more",
            "#load-more",
            ".more-link",
            "a.more",
            "[class*='load-more']",
            "[class*='loadmore']",
            "[id*='load-more']",
            "[id*='loadmore']"
        ]

        # Attempt to find and click load more button 1-3 times
        load_more_attempts = random.randint(1, 3)
        for attempt in range(load_more_attempts):
            try:
                # Scroll down to reveal load more button
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.9);")
                time.sleep(random.uniform(1, 2))

                # Try each selector
                for selector in load_more_selectors:
                    try:
                        load_more_buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                        if load_more_buttons:
                            for button in load_more_buttons:
                                # Check if button is visible and clickable
                                if button.is_displayed() and button.is_enabled():
                                    # Scroll to the button
                                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                                    time.sleep(random.uniform(0.5, 1))

                                    # Click the button
                                    button.click()
                                    log_message(f"google_bot_{bot_id}",
                                                f"Clicked 'load more' button (attempt {attempt + 1})")

                                    # Wait for new content to load
                                    time.sleep(random.uniform(3, 5))

                                    # Success, break out of the loop
                                    break
                    except Exception:
                        # If this selector doesn't work, try the next one
                        continue

                # Random delay between attempts
                time.sleep(random.uniform(2, 4))

            except Exception as e:
                log_message(f"google_bot_{bot_id}", f"Error clicking 'load more': {str(e)}")
                # Continue anyway - we'll work with what we have

        # After loading more articles, scroll back up a bit
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.3);")
        time.sleep(random.uniform(1, 2))

        # Find article links using multiple possible selectors
        article_selectors = [
            "div.post-item .image a",
            "article .entry-title a",
            ".blog-post a.read-more",
            ".article-title a",
            ".post a",
            "a.article",
            ".content-area a",
            "a[href*='article']",
            "a[href*='post']"
        ]

        articles = []
        for selector in article_selectors:
            found_elements = driver.find_elements(By.CSS_SELECTOR, selector)
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
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", article)
                    time.sleep(random.uniform(1, 2))

                    # Click the article
                    WebDriverWait(driver, 5).until(EC.element_to_be_clickable(article))
                    article.click()
                    log_message(f"google_bot_{bot_id}", f"Clicked on article: {article_url}")

                    # Simulate reading the article
                    simulate_human_reading(driver, bot_id)
                    return

                except (ElementNotInteractableException, TimeoutException) as e:
                    log_message(f"google_bot_{bot_id}", f"Skipping article due to error: {str(e)}")
                    continue  # Try the next article

            log_message(f"google_bot_{bot_id}", "No valid articles found to click.")

        else:
            # If no articles found, just browse the homepage
            simulate_human_reading(driver, bot_id)

    except Exception as e:
        log_message(f"google_bot_{bot_id}", f"Error while visiting website directly: {str(e)}", level="ERROR")

def simulate_human_reading(driver, bot_id="unknown"):
    """
    Simulate human reading behavior on a page.

    Args:
        driver: WebDriver instance
        bot_id: Identifier for this bot instance
    """
    # Determine reading time based on content length
    try:
        content_elements = driver.find_elements(By.CSS_SELECTOR, "p, h1, h2, h3, article, .content")
        content_length = sum(len(elem.text) for elem in content_elements if elem.text)

        # Adjust reading time based on content length
        base_time = random.uniform(8, 15)
        reading_time = min(base_time + (content_length / 1000), 45)  # Cap at 45 seconds
    except Exception:
        # Default reading time if content analysis fails
        reading_time = random.uniform(10, 20)

    log_message(f"google_bot_{bot_id}", f"Reading content for approximately {reading_time:.1f} seconds")

    # Scroll through the content gradually with random patterns
    scroll_positions = [20, 40, 60, 80, 100]  # Percentage of page height

    # Initial delay before starting to scroll
    time.sleep(random.uniform(2, 5))

    for position in scroll_positions:
        # Calculate scroll amount as percentage of page height
        scroll_amount = f"window.scrollTo(0, document.body.scrollHeight * {position/100});"
        driver.execute_script(scroll_amount)

        # Random reading delay at each position
        delay = reading_time / len(scroll_positions) * random.uniform(0.7, 1.3)
        time.sleep(delay)

        # Sometimes scroll up slightly to simulate re-reading
        if random.random() < 0.3:
            back_scroll = f"window.scrollBy(0, -{random.randint(100, 300)});"
            driver.execute_script(back_scroll)
            time.sleep(random.uniform(1, 3))

    # Sometimes click on internal links
    if random.random() < 0.3:
        try:
            internal_links = driver.find_elements(By.CSS_SELECTOR, "a[href^='/']")
            if internal_links:
                link = random.choice(internal_links)
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link)
                time.sleep(random.uniform(0.5, 1.5))
                link.click()
                time.sleep(random.uniform(5, 10))

                # Go back to previous page
                driver.back()
                time.sleep(random.uniform(2, 4))
        except Exception:
            pass


def run(config: Optional[Dict[str, Any]] = None, bot_config: Optional[Dict[str, Any]] = None):
    """
    Run the Google Traffic Bot with optional configuration.

    Args:
        config: Optional dictionary containing configuration parameters for search
        bot_config: Optional dictionary containing bot-specific configuration
    """
    bot_id = "unknown"
    proxy = None
    driver = None
    proxy_extension_path = None

    try:
        # Extract bot ID or proxy name if provided
        if bot_config and "proxy_name" in bot_config:
            bot_id = bot_config["proxy_name"].replace("google_bot_", "")

        # Load configuration if not provided
        if not config:
            # Get project root directory
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            config_path = os.path.join(project_root, 'configs', 'environment.json')
            config = load_config(config_path)

        # Get proxy bot name
        proxy_name = bot_config.get("proxy_name", "google_bot") if bot_config else "google_bot"

        # Set up Chrome WebDriver
        log_message(f"google_bot_{bot_id}", "Setting up Chrome WebDriver...")

        # Get proxy and create authentication extension
        proxy = get_proxy()
        proxy_extension_path = create_proxy_extension(proxy)

        # Log the proxy being used
        log_message(f"google_bot_{bot_id}", f"Using proxy: {proxy}")

        # Configure Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Use random window size and user agent to increase diversity
        viewport_width = random.choice([1366, 1440, 1920])
        viewport_height = random.choice([768, 900, 1080])
        chrome_options.add_argument(f"--window-size={viewport_width},{viewport_height}")

        # Set random user agent
        user_agent = get_random_user_agent()
        chrome_options.add_argument(f"user-agent={user_agent}")

        # Add proxy extension
        chrome_options.add_extension(proxy_extension_path)

        # Add language settings
        chrome_options.add_argument("--lang=en-US,en;q=0.9")

        # Disable automation flags
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)

        # Use WebDriverManager to manage ChromeDriver updates
        service = Service(ChromeDriverManager().install())

        # Initialize the Chrome WebDriver
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Execute CDP commands to prevent detection
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """
        })

        log_message(f"google_bot_{bot_id}", f"WebDriver set up successfully")

        # Extract configuration values
        target_website = config.get("target_website", "https://trants.me")

        # Get search keyword - either from config or generate from keywords and site filter
        search_keyword = None
        if "search_keyword" in config:
            search_keyword = config["search_keyword"]
        elif "keywords" in config and config["keywords"] and "site_filter" in config:
            keyword = random.choice(config["keywords"])
            site_filter = config["site_filter"]
            search_keyword = f"{keyword} {site_filter}"
        else:
            search_keyword = "site:trants.me"  # Fallback

        # Run the search
        found = search_google(driver, search_keyword, target_website, bot_id)

        # If not found, visit directly
        if not found:
            visit_website_directly(driver, target_website, bot_id)

        log_message(f"google_bot_{bot_id}", "Bot session completed successfully.")

    except Exception as e:
        log_message(f"google_bot_{bot_id}", f"Error during bot execution: {str(e)}", level="ERROR")

    finally:
        # Clean up resources
        if driver:
            driver.quit()

        # Remove temporary proxy extension file if it exists
        if proxy_extension_path and os.path.exists(proxy_extension_path):
            try:
                os.remove(proxy_extension_path)
            except Exception:
                pass


# For direct execution
if __name__ == "__main__":
    run()
