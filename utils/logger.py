import logging
import os
from datetime import datetime

# Define the directory where log files will be stored
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Generate log file name based on the current date
LOG_FILENAME = os.path.join(LOG_DIR, f"bot_log_{datetime.now().strftime('%Y-%m-%d')}.txt")

# Configure logging settings
logging.basicConfig(
    filename=LOG_FILENAME,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def log_message(message: str, level: str = "info") -> None:
    """
    Logs a message with a specified severity level.

    Args:
        message (str): The message content to be logged.
        level (str, optional): The severity level ('info' or 'error'). Defaults to 'info'.
    """
    log_levels = {
        "info": logging.info,
        "error": logging.error
    }

    # Retrieve the appropriate logging function based on level
    log_function = log_levels.get(level.lower(), logging.info)

    # Write the message to the log file
    log_function(message)

    # Display the log message in the console
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {level.upper()}: {message}")
