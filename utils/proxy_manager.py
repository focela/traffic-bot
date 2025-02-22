import os
import random
import requests

from utils.logger import log_message

# Add project paths to sys.path for module resolution
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def load_proxies():
    """
    Load proxy list from a configuration file.

    Reads the 'config/proxies.txt' file and returns a list of proxies.
    If the file is missing or empty, it logs an error message.

    Returns:
        list: A list of proxies or None if the file is missing or empty.
    """
    try:
        with open("config/proxies.txt", "r") as f:
            proxies = [line.strip() for line in f.readlines() if line.strip()]
        return proxies if proxies else None
    except FileNotFoundError:
        log_message("❌ Proxy configuration file 'config/proxies.txt' not found", "error")
        return None


def check_proxy(proxy):
    """
    Check if a proxy is functional by making a test request.

    Sends a request to 'https://httpbin.org/ip' to verify if the proxy is working.

    Args:
        proxy (str): The proxy address to test.

    Returns:
        bool: True if the proxy is working, False otherwise.
    """
    url = "https://httpbin.org/ip"
    proxies = {
        "http": f"http://{proxy}",
        "https": f"http://{proxy}",
    }

    try:
        response = requests.get(url, proxies=proxies, timeout=5)
        if response.status_code == 200:
            return True
    except requests.RequestException:
        pass

    return False


def get_valid_smartproxy():
    """
    Retrieve a valid proxy from the list.

    Iterates through the loaded proxy list, testing each one until a working proxy is found.
    Logs an error message if no valid proxy is available.

    Returns:
        str or None: A valid proxy string if found, otherwise None.
    """
    proxies = load_proxies()
    if not proxies:
        log_message("❌ No proxies loaded from file!", "error")
        return None

    for _ in range(len(proxies)):
        proxy = random.choice(proxies)
        if check_proxy(proxy):
            log_message(f"✅ Using valid proxy: {proxy}")
            return proxy

    log_message("❌ No working proxies found!", "error")
    return None
