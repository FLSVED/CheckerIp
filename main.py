import logging
import threading
from tkinter import Tk
from ui import IPTVApp
from config_manager import ConfigManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_server_connection(server_url, mac_address):
    logging.info(f"Testing connection to server: {server_url} with MAC: {mac_address}")
    # Implement actual connection test logic here
    return True

def run_analysis(config_manager):
    server_url = config_manager.get('server_url')
    mac_address = config_manager.get('mac_address')

    if not server_url or not mac_address:
        logging.error("Server URL or MAC address is missing in the configuration.")
        return

    if not test_server_connection(server_url, mac_address):
        logging.error("Failed to connect to the server.")
        return

    from subscriptions import SubscriptionManager
    manager = SubscriptionManager()
    # Replace with a valid method or remove if unnecessary
    # manager.load_default_subscriptions()

def setup_chromedriver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    try:
        service = Service()
        return webdriver.Chrome(service=service, options=options)
    except Exception as e:
        logging.error(f"Error setting up ChromeDriver: {e}")
        raise

def main():
    setup_logging()
    config_manager = ConfigManager()

    # Initialize chromedriver at the start
    try:
        driver = setup_chromedriver()
    except Exception as e:
        logging.error(f"Failed to initialize ChromeDriver: {e}")
        return

    root = Tk()
    app = IPTVApp(root, config_manager, driver)
    threading.Thread(target=run_analysis, args=(config_manager,), daemon=True).start()
    root.mainloop()

if __name__ == "__main__":
    main()
