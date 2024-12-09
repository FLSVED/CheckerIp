import re
import logging
import asyncio
from connection_to_server import ServerConnection

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
        for url in urls:
            for device in devices:
                asyncio.run(self.add_subscription_async(url, device['mac']))

    def parse_data(self, data):
        url_pattern = r'(http[^\s]+)'
        mac_pattern = r'([0-9A-Fa-f:]{17})'

        urls = re.findall(url_pattern, data)
        devices = []

        mac_matches = re.findall(mac_pattern, data)
        for mac in mac_matches:
            devices.append({'mac': mac, 'active': True})

        return urls, devices

    async def add_subscription_async(self, server_url, mac_address):
        """
        Ajoute un abonnement après validation de la connexion au serveur.

        :param server_url: URL du serveur
        :param mac_address: Adresse MAC à utiliser
        :return: Vrai si l'abonnement est ajouté, faux sinon
        """
        connection = ServerConnection(server_url, mac_address)
        if await connection.connect():
            if server_url not in self.subscriptions:
                self.subscriptions[server_url] = []
            self.subscriptions[server_url].append({
                'mac': mac_address,
                'active': True
            })
            return True
        return False

    async def manage_subscriptions_async(self, data):
        """
        Gère les abonnements en validant et ajoutant ceux qui sont connectables.

        :param data: Données contenant les URL et MAC à tester
        :return: Rapport et abonnements valides
        """
        urls, devices = self.parse_data(data)
        report = []
        
        for url in urls:
            for device in devices:
                if await self.add_subscription_async(url, device['mac']):
                    report.append(f"Connexion au serveur {url} réussie avec MAC {device['mac']}.")
                else:
                    report.append(f"Échec de la connexion au serveur {url} avec MAC {device['mac']}.")
                    
        return report, self.subscriptions

    async def check_connectivity_async(self):
        """
        Vérifie la connectivité de tous les abonnements et met à jour leur statut.
        """
        tasks = []
        for url, devices in self.subscriptions.items():
            for device in devices:
                tasks.append(self._check_device_connectivity_async(url, device))
        await asyncio.gather(*tasks)

    async def _check_device_connectivity_async(self, url, device):
        connection = ServerConnection(url, device['mac'])
        if not await connection.connect():
            self.connectivity_failures[device['mac']] = self.connectivity_failures.get(device['mac'], 0) + 1
            if self.connectivity_failures[device['mac']] >= 3:
                logging.warning(f"L'abonnement avec MAC {device['mac']} a été désactivé après 3 échecs de connexion.")
                device['active'] = False
        else:
            self.connectivity_failures[device['mac']] = 0

# Exemple d'utilisation
if __name__ == "__main__":
    manager = SubscriptionManager()
    asyncio.run(manager.manage_subscriptions_async(DEFAULT_SUBSCRIPTIONS))
    asyncio.run(manager.check_connectivity_async())
    for url, devices in manager.subscriptions.items():
        for device in devices:
            status = "actif" if device['active'] else "inactif"
            print(f"Abonnement {device['mac']} au serveur {url} est {status}.")