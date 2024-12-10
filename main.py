from tkinter import Tk
from ui import IPTVApp
from config_manager import ConfigManager
import logging

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    setup_logging()
    config_manager = ConfigManager()
    server_url = config_manager.get('server_url')
    mac_address = config_manager.get('mac_address')

    if not server_url or not mac_address:
        logging.error("Server URL or MAC address is missing in the configuration.")
        return
    
    root = Tk()
    app = IPTVApp(root, config_manager)
    root.mainloop()

if __name__ == "__main__":
    main()
