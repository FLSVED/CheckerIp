import json
from tkinter import Tk
from ui import IPTVApp
from config import load_config, get_server_url, get_mac_address, load_additional_sources

def main():
    config = load_config()
    server_url = get_server_url(config)
    mac_address = get_mac_address(config)
    
    if not server_url or not mac_address:
        server_url, mac_address = load_additional_sources()

    if not server_url or not mac_address:
        raise ValueError("Server URL or MAC address is missing in the configuration or additional sources.")
    
    root = Tk()
    app = IPTVApp(root, config, server_url, mac_address)
    root.mainloop()

if __name__ == "__main__":
    main()
