import re
import logging
from datetime import datetime
import aiohttp
import asyncio

__version__ = "1.1.0"

DEFAULT_SUBSCRIPTIONS = """
http://new.ivue.co:25461/c
    00:1A:79:70:E2:97 April 12, 2025, 4:34 pm
    00:1A:79:58:11:68 September 29, 2025, 11:00 pm
    00:1A:79:63:E8:E2 August 20, 2025, 6:37 pm
    00:1A:79:5C:87:23 January 20, 2025, 5:34 pm
    00:1A:79:59:C2:C5 February 3, 2025, 8:05 pm
    00:1A:79:B5:2B:14 February 20, 2025, 10:52 pm
    00:1A:79:54:88:37 January 28, 2025, 4:57 pm
    00:1A:79:B8:47:BD March 2, 2025, 7:56 pm
    00:1A:79:25:BD:13 April 12, 2025, 7:50 pm
    00:1A:79:CA:62:9A March 5, 2025, 1:53 pm
    00:1A:79:69:4F:57 February 6, 2025, 4:38 pm
    00:1A:79:75:33:75 February 23, 2025, 8:19 pm
    00:1A:79:B8:4D:1E August 17, 2025, 4:54 pm
    00:1A:79:B8:47:6F February 17, 2025, 5:50 pm
    00:1A:79:C6:E1:C2 April 28, 2025, 8:53 pm
    00:1A:79:BB:DD:10 May 3, 2025, 9:54 pm
    00:1A:79:6A:65:52 April 17, 2025, 1:47 pm
    00:1A:79:5A:57:43 January 2, 2025, 8:21 pm
    00:1A:79:7E:DB:16 April 15, 2025, 7:53 pm
    00:1A:79:2E:8A:C2 April 12, 2025, 2:03 pm
    00:1A:79:9A:19:78 April 2, 2025, 12:56 pm
    00:1A:79:5D:E0:FB February 22, 2025, 8:32 pm
    00:1A:79:42:78:51 March 28, 2025, 6:18 pm
    00:1A:79:08:80:6F February 17, 2025, 12:05 pm
"""

class SubscriptionManager:
    def __init__(self):
        self.subscriptions = {}
        self.connectivity_failures = {}
        self.load_default_subscriptions()

    def load_default_subscriptions(self):
        """Load the default subscriptions at startup."""
        urls, devices = self.parse_data(DEFAULT_SUBSCRIPTIONS)
        self.subscriptions = {url: devices for url in urls}

    def parse_data(self, data):
        url_pattern = r'(http[^\s]+)'
        mac_pattern = r'(?:(?:MAC\s*)?([0-9A-Fa-f:]+)\s*(?:\s*([\w\s.]+))?)'
        
        urls = re.findall(url_pattern, data)
        devices = []

        mac_matches = re.findall(mac_pattern, data)
        for mac, expiration_date_str in mac_matches:
            expiration_date = None
            if expiration_date_str:
                try:
                    expiration_date = datetime.strptime(expiration_date_str.strip(), '%B %d, %Y %I:%M %p')
                except ValueError:
                    try:
                        expiration_date = datetime.strptime(expiration_date_str.strip(), '%m.%d.%Y %I:%M %p')
                    except ValueError:
                        logging.warning(f"Date d'expiration non valide pour MAC {mac}: {expiration_date_str}")
                        expiration_date = None

            devices.append({
                'mac': mac,
                'expiration_date': expiration_date,
                'days_left': (expiration_date - datetime.now()).days if expiration_date else None,
                'active': True
            })

        return urls, devices

    async def validate_connection_async(self, url, mac):
        headers = {
            "User-Agent": "Mozilla/5.0",
            "X-MAC-Address": mac
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, timeout=5, headers=headers) as response:
                    return response.status == 200
            except aiohttp.ClientError as e:
                logging.error(f"Erreur de connexion à {url} avec MAC {mac}: {e}")
                return False

    async def manage_subscriptions_async(self, data):
        urls, devices = self.parse_data(data)
        report, valid_devices = await self.generate_report_async(urls, devices)

        for url in urls:
            if url in self.subscriptions:
                self.subscriptions[url].extend(valid_devices)
            else:
                self.subscriptions[url] = valid_devices
        return report, self.subscriptions

    async def generate_report_async(self, urls, devices):
        report = []
        valid_devices = []
        
        for url in urls:
            for device in devices:
                mac = device['mac']
                if await self.validate_connection_async(url, mac):
                    report.append(f"Connexion au serveur {url} réussie avec MAC {mac}.")
                    valid_devices.append(device)
                else:
                    report.append(f"Échec de la connexion au serveur {url} avec MAC {mac}.")
        
        return report, valid_devices

    async def check_connectivity_async(self):
        tasks = []
        for url, devices in self.subscriptions.items():
            for device in devices:
                mac = device['mac']
                tasks.append(self._check_device_connectivity(url, mac, device))
        await asyncio.gather(*tasks)

    async def _check_device_connectivity(self, url, mac, device):
        if not await self.validate_connection_async(url, mac):
            self.connectivity_failures[mac] = self.connectivity_failures.get(mac, 0) + 1
            if self.connectivity_failures[mac] >= 3:
                logging.warning(f"L'abonnement avec MAC {mac} a été désactivé après 3 échecs de connexion.")
                device['active'] = False
        else:
            self.connectivity_failures[mac] = 0