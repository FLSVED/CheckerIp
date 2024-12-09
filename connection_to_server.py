import aiohttp
import asyncio

class ServerConnection:
    def __init__(self, server_url, mac_address):
        self.server_url = server_url
        self.mac_address = mac_address
        self.headers = {"User-Agent": "IPTV Manager"}

    async def connect(self):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.server_url, headers=self.headers, timeout=20) as response:
                    if response.status == 200:
                        return True
            except aiohttp.ClientTimeout:
                print("Connection timed out.")
            except Exception as e:
                print(f"An error occurred: {e}")
        return False
