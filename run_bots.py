import os
import time
import random
from utils.logger import log_message


def run_bot(bot_name: str, script_name: str) -> None:
    """
    Execute a bot script and log its execution status.

    Args:
        bot_name (str): The display name of the bot.
        script_name (str): The script file name to execute.
    """
    log_message(f"🚀 Running {bot_name}...")
    os.system(f"python3 bots/{script_name}")
    log_message(f"✅ {bot_name} has completed execution!")


def main():
    """
    Main function to sequentially execute all bots with a random delay of 1-5 minutes between each.
    """
    bots = [
        ("Google Traffic Bot", "google_traffic.py"),
        ("Referral Traffic Bot", "referral_traffic.py"),
        ("AdSense Click Bot", "adsense_click.py")
    ]

    for bot_name, script_name in bots:
        run_bot(bot_name, script_name)

        # Add a delay of 1-5 minutes between each bot execution
        if bot_name != "AdSense Click Bot":
            delay = random.randint(60, 300)
            log_message(f"⏳ Waiting {delay // 60} minutes before running the next bot...")
            time.sleep(delay)

    log_message("✅ Completed execution of all bots!")


if __name__ == "__main__":
    main()
