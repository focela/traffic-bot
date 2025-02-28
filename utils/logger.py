import logging

logging.basicConfig(filename="bot_logs.txt", level=logging.INFO)

def log_message(bot_name, message):
    logging.info(f"[{bot_name}] {message}")
    print(f"[{bot_name}] {message}")
