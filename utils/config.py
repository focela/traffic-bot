"""
Optimized configuration module for Google Traffic Bot.

Provides configuration with separate keywords and site filter.
"""

import json
import os
import random


def load_config(config_file_path=None):
    """
    Load configuration with separate keywords and site filter.

    Args:
        config_file_path: Optional path to a JSON configuration file

    Returns:
        Dictionary containing the configuration
    """
    # Default configuration
    config = {
        "target_website": "https://trants.me",
        "site_filter": "site:trants.me",
        "keywords": ["AWS automation"],
        "search_keyword": "AWS automation site:trants.me"  # Assembled default
    }

    # Try loading from file if path is provided
    if config_file_path and os.path.exists(config_file_path):
        try:
            with open(config_file_path, 'r') as f:
                file_config = json.load(f)

                # Update basic config values if present
                for key in ["target_website", "site_filter"]:
                    if key in file_config:
                        config[key] = file_config[key]

                # Update keywords list if present
                if "keywords" in file_config and isinstance(file_config["keywords"], list):
                    config["keywords"] = file_config["keywords"]

        except Exception as e:
            print(f"Warning: Failed to load config file: {str(e)}")

    # Override with environment variables if present
    if os.environ.get('TARGET_WEBSITE'):
        config['target_website'] = os.environ.get('TARGET_WEBSITE')

    if os.environ.get('SITE_FILTER'):
        config['site_filter'] = os.environ.get('SITE_FILTER')

    # For keywords, we support comma-separated list in environment variable
    if os.environ.get('KEYWORDS'):
        keywords = os.environ.get('KEYWORDS').split(',')
        # Strip whitespace from each keyword
        keywords = [k.strip() for k in keywords if k.strip()]
        if keywords:
            config['keywords'] = keywords

    # Generate the search keyword only once during configuration loading
    config['search_keyword'] = generate_search_keyword(config)

    return config


def generate_search_keyword(config):
    """
    Generate a search keyword by combining a random keyword with the site filter.

    Args:
        config: Configuration dictionary containing keywords and site_filter

    Returns:
        Complete search keyword string
    """
    # Select a random keyword
    if "keywords" in config and config["keywords"]:
        keyword = random.choice(config["keywords"])
    else:
        keyword = ""

    # Combine with site filter
    site_filter = config.get("site_filter", "")

    # Assemble the complete search keyword
    if keyword and site_filter:
        return f"{keyword} {site_filter}"
    elif site_filter:
        return site_filter
    elif keyword:
        return keyword
    else:
        return ""  # Fallback to empty string
