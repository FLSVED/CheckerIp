import aiohttp
import logging
from error_handling import ConnectionError
import asyncio

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

    async def fetch_server_content(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.server_url, headers=self.headers) as response:
                if response.status == 200:
                    if response.content_type == 'application/json':
                        return await response.json()
                    else:
                        logging.error(f"Unexpected content type: {response.content_type}")
                        return None
                else:
                    logging.error(f"Failed to fetch server content: {response.status}")
                    return None
