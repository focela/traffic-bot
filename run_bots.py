import os
import time
import random
import threading
from utils.logger import log_message


def run_bot(bot_name: str, script_name: str) -> None:
    """
    Execute a bot script in a separate thread and log its execution status.

    Args:
        bot_name (str): The display name of the bot.
        script_name (str): The script file name to execute.
    """
    log_message(f"🚀 Running {bot_name}...")
    os.system(f"python3 bots/{script_name}")
    log_message(f"✅ {bot_name} has completed execution!")


def main():
    """
    Main function to execute 15 bots concurrently.
    """
    bots = [
        ("Google Traffic Bot", "google_traffic.py"),
        ("Referral Traffic Bot", "referral_traffic.py"),
        ("AdSense Click Bot", "adsense_click.py")
    ]

    num_threads = 15
    threads = []

    for _ in range(num_threads):
        for bot_name, script_name in bots:
            thread = threading.Thread(target=run_bot, args=(bot_name, script_name))
            threads.append(thread)
            thread.start()
            time.sleep(random.uniform(0.5, 2))

    for thread in threads:
        thread.join()

    log_message("🚀 All 15 bots have completed execution!")


if __name__ == "__main__":
    main()
