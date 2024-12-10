import requests

import logging


__version__ = "2.0.0"


class EpgManager:

def __init__(self):

self.epg_urls = []


def load_epg(self, epg_url):

try:

response = requests.get(epg_url)

response.raise_for_status()

logging.info(f"EPG chargé depuis {epg_url}")

return response.text

except requests.exceptions.RequestException as e:

logging.error(f"Erreur lors du chargement de l'EPG depuis {epg_url}: {e}")

return None


def add_epg_url(self, epg_url):

if epg_url and epg_url not in self.epg_urls:

self.epg_urls.append(epg_url)

logging.info(f"URL EPG ajoutée: {epg_url}")
