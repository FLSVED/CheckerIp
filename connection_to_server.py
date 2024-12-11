import aiohttp
import logging
from error_handling import ConnectionError
import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

class ServerConnection:
    def __init__(self, server_url, mac_address=None, headers=None):
        self.server_url = server_url
        self.mac_address = mac_address
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0',
            'X-MAC-Address': self.mac_address
        }

    async def connect(self):
        retries = 3
        for attempt in range(retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(self.server_url, headers=self.headers, timeout=60) as response:
                        logging.info(f"Response status: {response.status} for MAC {self.mac_address} at {self.server_url}")
                        if response.status == 200:
                            return True
                        else:
                            logging.warning(f"Non-200 status code: {response.status}")
                            return False
            except asyncio.TimeoutError:
                logging.error(f"Timeout error for MAC {self.mac_address} at {self.server_url}")
            except aiohttp.ClientError as e:
                logging.error(f"Client error for MAC {self.mac_address} at {self.server_url}: {e}")
            await asyncio.sleep(2 ** attempt)  # Exponential backoff

        raise ConnectionError(f"Failed to connect to {self.server_url} after {retries} attempts")

    def fetch_server_content(self):
        options = Options()
        options.headless = True
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        driver.get(self.server_url)
        content = driver.page_source
        driver.quit()
        return content
