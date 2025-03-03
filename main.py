"""
Main module for Traffic Bot Application.

This module manages the continuous execution of multiple traffic bots in parallel threads,
ensuring each bot instance uses random proxies from the pool and random search keywords.
"""

import copy
import os
import random
import signal
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

# Import bot modules
from bots import google_traffic_bot
from utils.config import load_config
from utils.logger import log_message

# Flag to control bot execution
running = True

# Configuration for bot execution
MAX_CONCURRENT_BOTS = 1  # Maximum number of bots to run concurrently
MIN_DELAY = 300  # Minimum delay between bot runs (seconds)
MAX_DELAY = 900  # Maximum delay between bot runs (seconds)
BOT_NAME = "main"  # Logger name for main process

# Bot instance locks to prevent proxy conflicts
bot_locks = {i: threading.Lock() for i in range(1, MAX_CONCURRENT_BOTS + 1)}


def load_bot_config():
    """
    Load configuration for bots with default values for target_website and keywords.

    Returns:
        Dictionary containing the configuration
    """
    # Get project root directory
    project_root = os.path.abspath(os.path.dirname(__file__))
    config_path = os.path.join(project_root, 'configs', 'environment.json')

    # Load configuration
    return load_config(config_path)


def signal_handler(sig, frame):
    """
    Handle termination signals to gracefully stop all bots.

    Args:
        sig: Signal number
        frame: Current stack frame
    """
    global running
    log_message(BOT_NAME, f"Received termination signal {sig}. Stopping all bots...")
    running = False
    # Allow time for threads to finish
    time.sleep(5)
    sys.exit(0)


def run_bot_with_unique_settings(bot_id: int) -> None:
    """
    Run a bot instance with unique proxy and randomized search keywords.

    Args:
        bot_id: Identifier for this bot instance
    """
    # Assign a proxy name to this bot instance - each bot will get a random proxy from google_bot pool
    proxy_name = f"google_bot_{bot_id}"

    # Load base configuration
    base_config = load_bot_config()

    log_message(BOT_NAME, f"Starting bot instance #{bot_id} with proxy_name: {proxy_name}")

    while running:
        try:
            # Create a unique configuration for this run
            run_config = copy.deepcopy(base_config)

            # Randomize search keyword for this run
            if "keywords" in run_config and run_config["keywords"]:
                keyword = random.choice(run_config["keywords"])
                site_filter = run_config.get("site_filter", "")

                if keyword and site_filter:
                    run_config["search_keyword"] = f"{keyword} {site_filter}"
                elif keyword:
                    run_config["search_keyword"] = keyword

                log_message(BOT_NAME, f"Bot #{bot_id} using keyword: {run_config['search_keyword']}")

            # Create custom bot config with proxy name
            custom_config = {
                "proxy_name": proxy_name
            }

            # Acquire lock for this bot to prevent conflicts
            with bot_locks[bot_id]:
                # Execute the bot with custom config
                log_message(BOT_NAME, f"Running bot instance #{bot_id} with proxy_name: {proxy_name}")
                google_traffic_bot.run(config=run_config, bot_config=custom_config)
                log_message(BOT_NAME, f"Bot instance #{bot_id} completed run")

            # Random delay before next run
            if running:
                # Use longer delays to reduce Google detection risk
                delay = random.uniform(MIN_DELAY, MAX_DELAY)
                log_message(BOT_NAME, f"Bot instance #{bot_id} waiting for {delay:.1f} seconds")

                # Sleep in small increments to check running flag
                sleep_increment = 5
                for _ in range(int(delay / sleep_increment) + 1):
                    if not running:
                        break
                    time.sleep(min(sleep_increment, delay))

        except Exception as e:
            log_message(BOT_NAME, f"Error in bot instance #{bot_id}: {str(e)}", level="ERROR")
            # Wait before retry on error
            time.sleep(30)  # Longer delay on error


def run_multiple_bots(num_bots: int = MAX_CONCURRENT_BOTS) -> None:
    """
    Run multiple bot instances concurrently with diverse settings.

    Args:
        num_bots: Number of bot instances to run
    """
    log_message(BOT_NAME, f"Starting {num_bots} bot instances in parallel")

    # Register signal handlers for graceful termination
    signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # termination signal

    # Create and start threads
    with ThreadPoolExecutor(max_workers=num_bots) as executor:
        # Submit bot tasks
        futures = []
        for i in range(1, num_bots + 1):
            future = executor.submit(run_bot_with_unique_settings, i)
            futures.append(future)
            # Stagger bot starts to avoid overwhelming resources and increase diversity
            time.sleep(random.uniform(5, 15))

        log_message(BOT_NAME, f"All {num_bots} bot instances are now running")

        # Wait for all futures to complete (never happens unless running becomes False)
        for future in futures:
            future.result()


def run_all_bots():
    """
    Main function to start all bots with diverse settings.
    """
    try:
        # Start multiple bot instances
        run_multiple_bots()
    except KeyboardInterrupt:
        log_message(BOT_NAME, "Keyboard interrupt received. Shutting down...")
    except Exception as e:
        log_message(BOT_NAME, f"Error in main process: {str(e)}", level="ERROR")
    finally:
        log_message(BOT_NAME, "Bot execution terminated")


if __name__ == "__main__":
    run_all_bots()