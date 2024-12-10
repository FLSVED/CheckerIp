import aiohttp
import logging
from error_handling import ConnectionError

class ServerConnection:

    def __init__(self, server_url, mac_address, headers=None):
        self.server_url = server_url
        self.mac_address = mac_address
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0',
            'X-MAC-Address': self.mac_address
        }

    async def connect(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.server_url, headers=self.headers, timeout=20) as response:
                    logging.info(f"Response status: {response.status} for MAC {self.mac_address} at {self.server_url}")
                    return response.status == 200
        except aiohttp.ClientError as e:
            logging.error(f"Client error for MAC {self.mac_address} at {self.server_url}: {e}")
            raise ConnectionError(f"Failed to connect to {self.server_url}") from e
