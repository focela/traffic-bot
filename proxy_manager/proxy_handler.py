import json
import random

def load_proxies():
    with open("data/proxies.json", "r") as file:
        return json.load(file)

def get_proxy(bot_name):
    proxies = load_proxies()
    if "proxy" in proxies[bot_name]:  # Static proxy
        return proxies[bot_name]["proxy"]
    else:
        return random.choice(proxies[bot_name]["proxy_pool"])
