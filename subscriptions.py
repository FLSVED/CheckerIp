import re
import logging
import asyncio
from connection_to_server import ServerConnection
from error_handling import ConnectionError

__version__ = "2.0.0"

DEFAULT_SUBSCRIPTIONS = """
http://new.ivue.co:25461/c
    00:1A:79:70:E2:97
    00:1A:79:58:11:68
    00:1A:79:63:E8:E2
    ...
"""

class SubscriptionManager:
    def __init__(self):
        self.subscriptions = {}
        self.connectivity_failures = {}
        self.load_default_subscriptions()

    def load_default_subscriptions(self):
        urls, devices = self.parse_data(DEFAULT_SUBSCRIPTIONS)
        if not urls or not devices:
            logging.warning("No default subscriptions found.")
            return
        asyncio.run(self.manage_subscriptions_async(DEFAULT_SUBSCRIPTIONS))

    def parse_data(self, data):
        url_pattern = r'(http[^\\s]+)'
        mac_pattern = r'([0-9A-Fa-f:]{17})'

        urls = re.findall(url_pattern, data)
        devices = [{'mac': mac, 'active': True} for mac in re.findall(mac_pattern, data)]

        return urls, devices

    async def add_subscription_async(self, server_url, mac_address):
        connection = ServerConnection(server_url, mac_address)
        try:
            if await connection.connect():
                if server_url not in self.subscriptions:
                    self.subscriptions[server_url] = []
                self.subscriptions[server_url].append({'mac': mac_address, 'active': True})
                return True
        except ConnectionError:
            logging.warning(f"Failed to connect to server {server_url} with MAC {mac_address}")
        return False

    async def manage_subscriptions_async(self, data):
        urls, devices = self.parse_data(data)
        tasks = [self.add_subscription_async(url, device['mac']) for url in urls for device in devices]
        results = await asyncio.gather(*tasks)
        logging.info(f"Subscription results: {results}")

    async def check_connectivity_async(self):
        tasks = []
        for url, devices in self.subscriptions.items():
            for device in devices:
                tasks.append(self._check_device_connectivity_async(url, device))
        await asyncio.gather(*tasks)

    async def _check_device_connectivity_async(self, url, device):
        connection = ServerConnection(url, device['mac'])
        try:
            if not await connection.connect():
                self.connectivity_failures[device['mac']] = self.connectivity_failures.get(device['mac'], 0) + 1
                if self.connectivity_failures[device['mac']] >= 3:
                    logging.warning(f"L'abonnement avec MAC {device['mac']} a été désactivé après 3 échecs de connexion.")
                    device['active'] = False
            else:
                self.connectivity_failures[device['mac']] = 0
        except ConnectionError:
            logging.error(f"Error checking connectivity for {device['mac']}")

if __name__ == "__main__":
    manager = SubscriptionManager()
    asyncio.run(manager.check_connectivity_async())