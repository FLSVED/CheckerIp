import aiohttp
import logging

class ServerConnection:
    def __init__(self, server_url, mac_address, headers=None):
        self.server_url = server_url
        self.mac_address = mac_address
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0',
            'X-MAC-Address': self.mac_address
        }

    async def connect(self):
        """
        Essaie de se connecter au serveur IPTV de manière asynchrone.

        :return: True si la connexion est réussie, False sinon
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.server_url, headers=self.headers, timeout=20) as response:
                    logging.info(f"Response status: {response.status} for MAC {self.mac_address} at {self.server_url}")
                    return response.status == 200
        except aiohttp.ClientTimeoutError:
            logging.error(f"Timeout error for MAC {self.mac_address} at {self.server_url}")
        except aiohttp.ClientConnectionError:
            logging.error(f"Connection error for MAC {self.mac_address} at {self.server_url}")
        except aiohttp.ClientResponseError as e:
            logging.error(f"Response error for MAC {self.mac_address} at {self.server_url}: {e}")
        except aiohttp.ClientError as e:
            logging.error(f"Client error for MAC {self.mac_address} at {self.server_url}: {e}")
        return False

    def update_headers(self, new_headers):
        """
        Met à jour les en-têtes de la connexion.

        :param new_headers: Dictionnaire contenant les nouveaux en-têtes
        """
        self.headers.update(new_headers)
