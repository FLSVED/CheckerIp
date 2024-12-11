import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def run_test():
    """Test fetching URL and cookie using Chrome Driver."""
    logging.basicConfig(level=logging.INFO)
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    try:
        # Ensure the path to chromedriver.exe is correctly specified
        service = Service("C:/Users/pc/chromedriver/chromedriver.exe")
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        logging.error(f"Error setting up ChromeDriver: {e}")
        raise

    test_url = 'https://www.google.com/'
    expected_title = 'Google'
    domain = '.google.com'

    try:
        driver.get(test_url)
        logging.info('Expected tab title: %s. Got: %s', expected_title, driver.title)
        if driver.title != expected_title:
            raise Exception(f'Getting title failed, got title: {driver.title}')
        cookie_found = any(cookie for cookie in driver.get_cookies() if cookie['domain'] == domain)
        if not cookie_found:
            raise Exception(f'Expected cookie for {test_url}. Found: {[c["domain"] for c in driver.get_cookies()]}')
    finally:
        driver.quit()

if __name__ == "__main__":
    run_test()
