python
import re
import logging
from datetime import datetime
import aiohttp
import asyncio

__version__ = "1.0.0"

class SubscriptionManager:
    def __init__(self):
        self.subscriptions = {}
        self.connectivity_failures = {}

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

        self.subscriptions = {url: valid_devices for url in urls}
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
