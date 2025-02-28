"""
Proxy Handler Module - Manages proxy configuration for web automation.

This module provides functionalities to load proxy configurations from a JSON file,
select appropriate proxies based on bot names, and create Chrome extensions for proxy authentication.
"""

import json
import os
import random
import urllib.parse
import zipfile
from typing import Dict, Union, List, Optional


class ProxyHandler:
    """Handles proxy configuration and management for web automation bots."""

    def __init__(self, proxy_config_path: str = "configs/proxies.json"):
        """
        Initialize the ProxyHandler with a path to proxy configuration.

        Args:
            proxy_config_path: Path to the JSON file containing proxy configurations
        """
        self.proxy_config_path = proxy_config_path
        self.proxies = None

    def load_proxies(self) -> Dict:
        """
        Load proxy configurations from the JSON file.

        Returns:
            Dictionary containing proxy configurations for different bots
        """
        if self.proxies is None:
            try:
                with open(self.proxy_config_path, "r") as file:
                    self.proxies = json.load(file)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                raise Exception(f"Failed to load proxy configuration: {str(e)}")

        return self.proxies

    def get_proxy(self, bot_name: str) -> str:
        """
        Get a proxy URL for the specified bot.

        Args:
            bot_name: Name of the bot to get proxy for

        Returns:
            Proxy URL string

        Raises:
            KeyError: If the bot name is not found in the configuration
        """
        proxies = self.load_proxies()

        if bot_name not in proxies:
            raise KeyError(f"Bot name '{bot_name}' not found in proxy configuration")

        bot_config = proxies[bot_name]

        # Return static proxy if configured
        if "proxy" in bot_config:
            return bot_config["proxy"]
        # Otherwise return a random proxy from the pool
        elif "proxy_pool" in bot_config and bot_config["proxy_pool"]:
            return random.choice(bot_config["proxy_pool"])
        else:
            raise ValueError(f"No valid proxy configuration found for bot '{bot_name}'")

    def create_proxy_extension(self, proxy_url: str, output_path: str = None) -> str:
        """
        Creates a Chrome extension for proxy authentication.

        Args:
            proxy_url: Proxy URL with authentication details
            output_path: Optional path to save the extension zip file

        Returns:
            Path to the created proxy extension zip file
        """
        # Parse the proxy URL to extract components
        parsed_proxy = urllib.parse.urlparse(proxy_url)

        if not parsed_proxy.hostname or not parsed_proxy.port:
            raise ValueError("Invalid proxy URL format. Expected format: http(s)://username:password@hostname:port")

        # Define the extension manifest
        manifest_json = """{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Proxy Authentication Extension",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    }
}"""

        # Define the background script with proxy configuration
        background_js = f"""
var config = {{
    mode: "fixed_servers",
    rules: {{
        singleProxy: {{
            scheme: "http",
            host: "{parsed_proxy.hostname}",
            port: parseInt("{parsed_proxy.port}")
        }},
        bypassList: []
    }}
}};

chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});

chrome.webRequest.onAuthRequired.addListener(
    function(details) {{
        return {{
            authCredentials: {{
                username: "{parsed_proxy.username}",
                password: "{parsed_proxy.password}"
            }}
        }};
    }},
    {{urls: ["<all_urls>"]}},
    ["blocking"]
);
"""

        # Determine the output file path
        plugin_file = output_path if output_path else "proxy_auth_plugin.zip"

        # Create the zip file containing the extension
        with zipfile.ZipFile(plugin_file, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)

        return plugin_file


# For backwards compatibility
proxy_handler = ProxyHandler()


def load_proxies() -> Dict:
    """
    Load proxy configurations from the default JSON file.

    Returns:
        Dictionary containing proxy configurations
    """
    return proxy_handler.load_proxies()


def get_proxy(bot_name: str) -> str:
    """
    Get a proxy URL for the specified bot.

    Args:
        bot_name: Name of the bot to get proxy for

    Returns:
        Proxy URL string
    """
    return proxy_handler.get_proxy(bot_name)


def create_proxy_extension(proxy_url: str, output_path: str = None) -> str:
    """
    Creates a Chrome extension for proxy authentication.

    Args:
        proxy_url: Proxy URL with authentication details
        output_path: Optional path to save the extension zip file

    Returns:
        Path to the created proxy extension zip file
    """
    return proxy_handler.create_proxy_extension(proxy_url, output_path)