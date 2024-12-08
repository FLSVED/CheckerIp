import re
import logging
import aiohttp
import asyncio

__version__ = "1.1.0"

DEFAULT_SUBSCRIPTIONS = """
http://new.ivue.co:25461/c
    00:1A:79:70:E2:97
    00:1A:79:58:11:68
    00:1A:79:63:E8:E2
    00:1A:79:5C:87:23
    00:1A:79:59:C2:C5
    00:1A:79:B5:2B:14
    00:1A:79:54:88:37
    00:1A:79:B8:47:BD
    00:1A:79:25:BD:13
    00:1A:79:CA:62:9A
    00:1A:79:69:4F:57
    00:1A:79:75:33:75
    00:1A:79:B8:4D:1E
    00:1A:79:B8:47:6F
    00:1A:79:C6:E1:C2
    00:1A:79:BB:DD:10
    00:1A:79:6A:65:52
    00:1A:79:5A:57:43
    00:1A:79:7E:DB:16
    00:1A:79:2E:8A:C2
    00:1A:79:9A:19:78
    00:1A:79:5D:E0:FB
    00:1A:79:42:78:51
    00:1A:79:08:80:6F
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
        mac_pattern = r'([0-9A-Fa-f:]{17})'

        urls = re.findall(url_pattern, data)
        devices = []

        mac_matches = re.findall(mac_pattern, data)
        for mac in mac_matches:
            devices.append({
                'mac': mac,
                'active': True
            })

        return urls, devices

    async def validate_connection_async(self, url, mac, retries=3):
        headers = {
            "User-Agent": "Mozilla/5.0",
            "X-MAC-Address": mac
        }
        for attempt in range(retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=10, headers=headers) as response:
                        if response.status == 200:
                            return True
            except aiohttp.ClientError as e:
                logging.error(f"Erreur de connexion à {url} avec MAC {mac}: {e}")
            await asyncio.sleep(2)  # Wait before retrying
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
        
