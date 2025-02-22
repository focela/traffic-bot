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
    Main function to sequentially execute all bots with random delays in an infinite loop.
    """
    bots = [
        ("Google Traffic Bot", "google_traffic.py"),
        ("Referral Traffic Bot", "referral_traffic.py"),
        ("AdSense Click Bot", "adsense_click.py")
    ]

    while True:
        for bot_name, script_name in bots:
            run_bot(bot_name, script_name)

            # Add delay between bot executions except for the last bot
            if bot_name != "AdSense Click Bot":
                delay = random.randint(300, 600)
                log_message(f"⏳ Waiting {delay // 60} minutes before running the next bot...")
                time.sleep(delay)

        # Wait before restarting the loop
        loop_delay = random.randint(600, 900)
        log_message(f"🔄 Restarting the bot loop in {loop_delay // 60} minutes...")
        time.sleep(loop_delay)


if __name__ == "__main__":
    main()
