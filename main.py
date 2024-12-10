from tkinter import Tk
from ui import IPTVApp
from config_manager import ConfigManager
import logging
import threading

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_analysis(config_manager):
    server_url = config_manager.get('server_url')
    mac_address = config_manager.get('mac_address')
    
    if not server_url or not mac_address:
        logging.error("Server URL or MAC address is missing in the configuration.")
        return
    
    # Assuming SubscriptionManager is what runs the analysis
    from subscriptions import SubscriptionManager
    manager = SubscriptionManager()
    manager.load_default_subscriptions()

def main():
    setup_logging()
    config_manager = ConfigManager()

    root = Tk()
    app = IPTVApp(root, config_manager)
    threading.Thread(target=run_analysis, args=(config_manager,), daemon=True).start()
    root.mainloop()

if __name__ == "__main__":
    main()
