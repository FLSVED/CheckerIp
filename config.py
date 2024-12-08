import json
import os
import requests
import pyperclip

__version__ = "1.0.0"

def load_config(file_path=None):
    if file_path is None:
        # Use the absolute path to ensure the file can be found
        file_path = os.path.join(os.path.dirname(__file__), 'config.json')

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Configuration file {file_path} not found.")

    with open(file_path, 'r') as f:
        return json.load(f)

def get_server_url(config):
    return config.get('server_url')

def get_mac_address(config):
    return config.get('mac_address')

def load_additional_sources():
    server_url = None
    mac_address = None

    # Try to load from clipboard
    try:
        clipboard_data = pyperclip.paste()
        if clipboard_data:
            server_url, mac_address = clipboard_data.split(',')
    except Exception as e:
        print(f"Error loading from clipboard: {e}")

    # Try to load from a file
    if not server_url or not mac_address:
        try:
            with open('server_mac.txt', 'r') as f:
                lines = f.readlines()
                if lines:
                    server_url, mac_address = lines[0].strip().split(',')
        except Exception as e:
            print(f"Error loading from file: {e}")

    # Try to load from a webpage
    if not server_url or not mac_address:
        try:
            response = requests.get('http://example.com/get_server_mac')
            if response.status_code == 200:
                server_url, mac_address = response.text.split(',')
        except Exception as e:
            print(f"Error loading from webpage: {e}")

    return server_url, mac_address
