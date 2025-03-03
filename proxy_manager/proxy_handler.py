"""
Proxy Handler Module - Manages proxy configuration for web automation.

This module provides functionalities to load proxy configurations from a TXT file,
select random proxies, and create Chrome extensions for proxy authentication.
"""

import os
import random
import urllib.parse
import zipfile
from typing import Dict, List, Optional


class ProxyHandler:
    """Handles proxy configuration and management for web automation bots."""

    def __init__(self, proxy_file_path: str = "configs/proxy.txt"):
        """
        Initialize the ProxyHandler with a path to proxy configuration.

        Args:
            proxy_file_path: Path to the TXT file containing proxy configurations
        """
        self.proxy_file_path = proxy_file_path
        self.proxies = None

    def load_proxies(self) -> List[str]:
        """
        Load proxy configurations from a text file.
        Expected format: hostname:port:username:password in each line

        Returns:
            List of proxy URLs
        """
        if self.proxies is None:
            proxy_list = []

            try:
                with open(self.proxy_file_path, "r") as file:
                    for line in file:
                        line = line.strip()
                        if not line:
                            continue

                        parts = line.split(':')
                        if len(parts) >= 4:
                            hostname = parts[0]
                            port = parts[1]
                            username = parts[2]
                            # Join remaining parts with ':' in case password contains colons
                            password = ':'.join(parts[3:])

                            # Create proxy URL
                            proxy_url = f"http://{username}:{password}@{hostname}:{port}"
                            proxy_list.append(proxy_url)

                self.proxies = proxy_list

            except FileNotFoundError as e:
                raise Exception(f"Failed to load proxy configuration: {str(e)}")

        return self.proxies

    def get_proxy(self) -> str:
        """
        Get a random proxy URL from the loaded proxies.

        Returns:
            Proxy URL string

        Raises:
            ValueError: If no proxies are available
        """
        proxies = self.load_proxies()

        if not proxies:
            raise ValueError("No proxies available in the configuration file")

        return random.choice(proxies)

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


# Global instance for convenience
proxy_handler = ProxyHandler()


def load_proxies() -> List[str]:
    """
    Load proxy configurations from the default TXT file.

    Returns:
        List of proxy URLs
    """
    return proxy_handler.load_proxies()


def get_proxy() -> str:
    """
    Get a random proxy from the default configuration.

    Returns:
        Proxy URL string
    """
    return proxy_handler.get_proxy()


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


def init_proxy_handler(proxy_file_path: str) -> ProxyHandler:
    """
    Initialize the global proxy handler with a specific TXT file.

    Args:
        proxy_file_path: Path to the TXT file containing proxy configurations

    Returns:
        ProxyHandler instance
    """
    global proxy_handler
    proxy_handler = ProxyHandler(proxy_file_path)
    return proxy_handler