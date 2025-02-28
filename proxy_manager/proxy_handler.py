import json
import random
import zipfile
import os
import urllib.parse

def load_proxies():
    with open("data/proxies.json", "r") as file:
        return json.load(file)

def get_proxy(bot_name):
    proxies = load_proxies()
    if "proxy" in proxies[bot_name]:  # Static proxy
        return proxies[bot_name]["proxy"]
    else:
        return random.choice(proxies[bot_name]["proxy_pool"])

def create_proxy_extension(proxy_url):
    """Creates a Chrome extension for proxy authentication."""
    parsed_proxy = urllib.parse.urlparse(proxy_url)
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Proxy Authentication Extension",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        }
    }
    """

    background_js = f"""
    var config = {{
        mode: "fixed_servers",
        rules: {{
          singleProxy: {{
            scheme: "http",
            host: "{parsed_proxy.hostname}",
            port: parseInt("{parsed_proxy.port}")
          }},
          bypassList: []
        }}
    }};
    chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});

    chrome.webRequest.onAuthRequired.addListener(
        function(details) {{
            return {{
                authCredentials: {{
                    username: "{parsed_proxy.username}",
                    password: "{parsed_proxy.password}"
                }}
            }};
        }},
        {{urls: ["<all_urls>"]}},
        ["blocking"]
    );
    """

    pluginfile = "proxy_auth_plugin.zip"
    with zipfile.ZipFile(pluginfile, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)

    return pluginfile
