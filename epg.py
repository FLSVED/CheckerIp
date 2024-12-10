import requests
import logging
import zipfile
import os
import xml.etree.ElementTree as ET

__version__ = "2.0.0"

class EpgManager:

    def __init__(self):
        self.epg_urls = []

    def download_and_extract_zip(self, url, extract_to='xmltv_data'):
        try:
            # Step 1: Download the zip file
            response = requests.get(url)
            response.raise_for_status()
            zip_path = os.path.join(extract_to, 'xmltv.zip')
            os.makedirs(extract_to, exist_ok=True)
            with open(zip_path, 'wb') as f:
                f.write(response.content)
            logging.info(f"Downloaded zip file from {url}")

            # Step 2: Decompress the zip file
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            logging.info(f"Extracted zip file to {extract_to}")
            os.remove(zip_path)  # Clean up zip file after extraction

            # Step 3: Process the XML files
            self.process_epg_files(extract_to)

        except requests.exceptions.RequestException as e:
            logging.error(f"Erreur lors du téléchargement du fichier zip depuis {url}: {e}")
        except zipfile.BadZipFile as e:
            logging.error(f"Erreur lors de la décompression du fichier zip: {e}")

    def process_epg_files(self, directory):
        for filename in os.listdir(directory):
            if filename.endswith(".xml"):
                file_path = os.path.join(directory, filename)
                self.parse_epg_file(file_path)

    def parse_epg_file(self, file_path):
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            for channel in root.findall('channel'):
                channel_id = channel.get('id')
                for programme in root.findall(f"programme[@channel='{channel_id}']"):
                    start = programme.get('start')
                    stop = programme.get('stop')
                    title = programme.find('title').text
                    logging.info(f"Channel: {channel_id}, Start: {start}, Stop: {stop}, Title: {title}")
        except ET.ParseError as e:
            logging.error(f"Erreur lors de l'analyse du fichier XML {file_path}: {e}")

    def load_epg(self, epg_url):
        self.download_and_extract_zip(epg_url)

    def add_epg_url(self, epg_url):
        if epg_url and epg_url not in self.epg_urls:
            self.epg_urls.append(epg_url)
            logging.info(f"URL EPG ajoutée: {epg_url}")
