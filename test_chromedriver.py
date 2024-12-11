import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def run_test():
    """Test fetching URL and cookie using Chrome Driver."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    try:
        service = Service()
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
            raise Exception('Getting title failed, got title: %s' % driver.title)
        cookie_found = any([
                cookie for cookie in driver.get_cookies()
                if cookie['domain'] == domain
        ])
        if not cookie_found:
            raise Exception(
                    'Expected cookie for %s. Found: %s' %
                    (test_url, [c['domain'] for c in driver.get_cookies()]))
    finally:
        driver.quit()
