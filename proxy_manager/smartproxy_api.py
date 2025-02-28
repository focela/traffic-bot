import requests

SMARTPROXY_URL = "https://api.smartproxy.com/v1/proxies"
AUTH = ("your_username", "your_password")

def rotate_proxy():
    response = requests.get(SMARTPROXY_URL, auth=AUTH)
    new_ip = response.json().get("proxy_ip")
    return new_ip
