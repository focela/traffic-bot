"""
SmartProxy API Module - Provides functionalities for interacting with SmartProxy's API.

This module handles communication with the SmartProxy API for rotating proxies, 
managing IP addresses, and other related proxy operations in a production environment.
"""

import os
import logging
import requests
from typing import Dict, Tuple, Optional, Union, Any
from requests.exceptions import RequestException, Timeout, ConnectionError

# Configure logging
logger = logging.getLogger(__name__)


class SmartProxyAPIConfig:
    """Configuration class for SmartProxy API credentials and settings."""

    # Default API endpoints
    BASE_URL = "https://api.smartproxy.com/v1"
    PROXIES_ENDPOINT = "/proxies"

    # Environment variable names for configuration
    ENV_USERNAME = "SMARTPROXY_USERNAME"
    ENV_PASSWORD = "SMARTPROXY_PASSWORD"
    ENV_API_KEY = "SMARTPROXY_API_KEY"

    @classmethod
    def get_auth(cls) -> Tuple[str, str]:
        """
        Get authentication credentials from environment variables.

        Returns:
            Tuple containing username and password

        Raises:
            ValueError: If required environment variables are not set
        """
        username = os.environ.get(cls.ENV_USERNAME)
        password = os.environ.get(cls.ENV_PASSWORD)

        if not username or not password:
            raise ValueError(
                f"SmartProxy credentials not found. Please set {cls.ENV_USERNAME} and {cls.ENV_PASSWORD} "
                "environment variables."
            )

        return (username, password)

    @classmethod
    def get_api_key(cls) -> Optional[str]:
        """
        Get API key from environment variables.

        Returns:
            API key string or None if not set
        """
        return os.environ.get(cls.ENV_API_KEY)


class SmartProxyAPI:
    """Client for interacting with SmartProxy's API."""

    def __init__(self, timeout: int = 10, max_retries: int = 3):
        """
        Initialize the SmartProxy API client.

        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts for failed requests
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.base_url = SmartProxyAPIConfig.BASE_URL

        # Get authentication credentials
        try:
            self.auth = SmartProxyAPIConfig.get_auth()
            self.api_key = SmartProxyAPIConfig.get_api_key()
        except ValueError as e:
            logger.error(f"Authentication configuration error: {str(e)}")
            raise

    def _prepare_headers(self) -> Dict[str, str]:
        """
        Prepare request headers including API key if available.

        Returns:
            Dictionary containing request headers
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        return headers

    def _make_request(self,
                      method: str,
                      endpoint: str,
                      params: Optional[Dict] = None,
                      data: Optional[Dict] = None) -> Dict:
        """
        Make an HTTP request to the SmartProxy API with retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint to call
            params: Optional query parameters
            data: Optional request body

        Returns:
            Response data as dictionary

        Raises:
            RequestException: If the request fails after all retries
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._prepare_headers()

        for attempt in range(self.max_retries):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    auth=self.auth,
                    headers=headers,
                    params=params,
                    json=data,
                    timeout=self.timeout
                )

                response.raise_for_status()
                return response.json()

            except (ConnectionError, Timeout) as e:
                logger.warning(f"Network error on attempt {attempt + 1}/{self.max_retries}: {str(e)}")
                if attempt == self.max_retries - 1:
                    logger.error(f"Request failed after {self.max_retries} attempts: {str(e)}")
                    raise

            except RequestException as e:
                logger.error(f"API request failed: {str(e)}")
                if hasattr(e.response, 'text'):
                    logger.error(f"Response details: {e.response.text}")
                raise

    def rotate_proxy(self) -> str:
        """
        Request a new proxy IP from SmartProxy's rotation service.

        Returns:
            New proxy IP address

        Raises:
            ValueError: If the API response doesn't contain a proxy IP
        """
        try:
            response_data = self._make_request(
                method="GET",
                endpoint=SmartProxyAPIConfig.PROXIES_ENDPOINT
            )

            new_ip = response_data.get("proxy_ip")
            if not new_ip:
                raise ValueError("No proxy IP received from SmartProxy API")

            logger.info(f"Successfully rotated to new proxy IP: {new_ip}")
            return new_ip

        except Exception as e:
            logger.error(f"Failed to rotate proxy: {str(e)}")
            raise


# For backwards compatibility with existing code
def rotate_proxy() -> str:
    """
    Request a new proxy IP from SmartProxy's rotation service.

    Returns:
        New proxy IP address

    Note:
        This function maintains backwards compatibility with existing code.
        For new implementations, consider using the SmartProxyAPI class directly.
    """
    api = SmartProxyAPI()
    return api.rotate_proxy()
