print("Script is starting...")
import sys
import os

# Afficher un message de démarrage
print("Démarrage du script...")

# Afficher la version de Python utilisée
print(f"Version de Python: {sys.version}")

# Afficher le chemin d'exécution du script
print(f"Chemin du script: {os.path.abspath(__file__)}")

# Afficher le répertoire courant
print(f"Répertoire courant: {os.getcwd()}")

# Afficher les arguments de la ligne de commande (s'il y en a)
print(f"Arguments de la ligne de commande: {sys.argv}")

import re
import requests
import vlc
import time
import logging
from datetime import datetime
from tkinter import Tk, Listbox, Button, Scrollbar, END, messagebox, StringVar, Entry, Label, Frame, Toplevel, ttk
import threading
import pytz
import pyperclip  # Pour gérer le presse-papiers

# Configurer la journalisation
logging.basicConfig(filename='iptv_manager.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

class IPTVManager:
    def __init__(self):
        self.subscriptions = {}
        self.favorites = []
        self.history = []
        self.vod_list = []  # Liste pour gérer les VOD
        self.channels = []  # Liste des chaînes fusionnées
        self.connectivity_failures = {}  # Pour suivre les échecs de connectivité
    
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
                'active': True  # Par défaut, tous les abonnements sont actifs
            })

        return urls, devices

    def validate_connection(self, url, mac):
        headers = {
            "User-Agent": "Mozilla/5.0",
            "X-MAC-Address": mac  # Ajout de l'adresse MAC dans les en-têtes
        }
        
        try:
            response = requests.get(url, timeout=5, headers=headers)
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            logging.error(f"Erreur de connexion à {url} avec MAC {mac}: {e}")
            return False

    def test_stream(self, stream_url, mac):
        try:
            headers = {"X-MAC-Address": mac}
            instance = vlc.Instance()
            player = instance.media_player_new()
            media = instance.media_new(stream_url)
            media.get_mrl()
            player.set_media(media)

            player.play()
            time.sleep(5)  # Attend 5 secondes pour voir si le flux démarre
            state = player.get_state()
            player.stop()
            
            return state == vlc.State.Playing
        except Exception as e:
            logging.error(f"Erreur lors du test du flux {stream_url} avec MAC {mac}: {e}")
            return False

    def analyze_stream(self, stream_url, mac):
        logging.info(f"Analyse du flux {stream_url} en cours avec MAC {mac}...")
        if self.test_stream(stream_url, mac):
            logging.info(f"Le flux pour {stream_url} est valide.")
            return True
        else:
            logging.warning(f"Le flux {stream_url} est inaccessible.")
            return False

    def generate_report(self, urls, devices):
        report = []
        valid_devices = []
        
        for url in urls:
            for device in devices:
                mac = device['mac']
                if self.validate_connection(url, mac):
                    report.append(f"Connexion au serveur {url} réussie avec MAC {mac}.")
                    stream_url = f"{url}/{mac}"
                    if self.test_stream(stream_url, mac):
                        report.append(f"Le flux pour {mac} est valide et en cours de lecture.")
                        valid_devices.append({'mac': mac, 'url': stream_url, 'country': 'FR', 'active': device['active']})
                    else:
                        report.append(f"Impossible de lire le flux pour {mac}.")
                else:
                    report.append(f"Échec de la connexion au serveur {url} avec MAC {mac}.")
        
        return report, valid_devices

    def manage_subscriptions(self, data):
        urls, devices = self.parse_data(data)
        report, valid_devices = self.generate_report(urls, devices)

        self.subscriptions = {url: valid_devices for url in urls}
        self.channels = self.merge_channels()

        for line in report:
            logging.info(line)

    def load_subscriptions_from_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                data = file.read()
            self.manage_subscriptions(data)
        except FileNotFoundError:
            logging.error(f"Fichier {file_path} non trouvé.")
            messagebox.showerror("Erreur", f"Fichier {file_path} non trouvé.")

    def load_subscriptions_from_clipboard(self):
        try:
            data = pyperclip.paste()
            self.manage_subscriptions(data)
            messagebox.showinfo("Info", "Les abonnements ont été chargés depuis le presse-papiers.")
        except Exception as e:
            logging.error(f"Erreur lors du chargement du presse-papiers: {e}")
            messagebox.showerror("Erreur", "Impossible de charger les abonnements depuis le presse-papiers.")

    def merge_channels(self):
        merged_channels = []
        for devices in self.subscriptions.values():
            for device in devices:
                if device['active']:
                    merged_channels.append(device)
        # Sorting to prioritize French channels
        merged_channels.sort(key=lambda x: (x['country'] != 'FR', x['mac']))
        return merged_channels

    def switch_subscription(self, current_mac, new_url):
        for url, devices in self.subscriptions.items():
            for device in devices:
                if device['mac'] == current_mac:
                    print(f"Changement de l'abonnement de {url} à {new_url} pour le flux {current_mac}.")
                    return
        print("Flux non trouvé dans les abonnements.")

    def add_to_favorites(self, item):
        if item not in self.favorites:
            self.favorites.append(item)
            logging.info(f"Ajouté aux favoris: {item}")
            messagebox.showinfo("Info", f"{item} a été ajouté aux favoris.")
        else:
            messagebox.showwarning("Avertissement", f"{item} est déjà dans les favoris.")

    def view_history(self):
        return self.history

    def add_to_history(self, item):
        if item not in self.history:
            self.history.append(item)
            logging.info(f"Ajouté à l'historique: {item}")

    def load_vod(self, vod_data):
        self.vod_list = vod_data.splitlines()

    def search_vod(self, query):
        return [vod for vod in self.vod_list if query.lower() in vod.lower()]

    def switch_channel(self, current_mac, new_server_url):
        for url, devices in self.subscriptions.items():
            for device in devices:
                if device['mac'] == current_mac:
                    new_stream_url = f"{new_server_url}/{current_mac}"
                    if self.test_stream(new_stream_url, current_mac):
                        return new_stream_url
        return None

    def auto_switch_channel(self, current_mac):
        best_stream_url = None
        best_quality = 0  # Placeholder for quality comparison logic

        for url, devices in self.subscriptions.items():
            for device in devices:
                if device['mac'] == current_mac:
                    stream_url = f"{url}/{current_mac}"
                    if self.test_stream(stream_url, current_mac):
                        # Placeholder logic for quality check
                        current_quality = 1  # Replace with actual quality check logic
                        if current_quality > best_quality:
                            best_quality = current_quality
                            best_stream_url = stream_url

        return best_stream_url

    def cast_to_device(self, stream_url, device_name):
        try:
            # Placeholder for actual casting logic
            print(f"Casting {stream_url} to {device_name}")
            logging.info(f"Casting {stream_url} to {device_name}")
        except Exception as e:
            logging.error(f"Erreur lors du casting vers {device_name}: {e}")

    def check_connectivity(self):
        """Check connectivity to each server and disable if necessary."""
        for url, devices in self.subscriptions.items():
            for device in devices:
                mac = device['mac']
                if not self.validate_connection(url, mac):
                    self.connectivity_failures[mac] = self.connectivity_failures.get(mac, 0) + 1
                    if self.connectivity_failures[mac] >= 3:
                        logging.warning(f"L'abonnement avec MAC {mac} a été désactivé après 3 échecs de connexion.")
                        devices.remove(device)  # Supprimer le serveur après 3 échecs de connexion
                else:
                    self.connectivity_failures[mac] = 0  # Reset counter if successful

    def toggle_subscription(self, mac, active):
        """Manually activate or deactivate a subscription."""
        for url, devices in self.subscriptions.items():
            for device in devices:
                if device['mac'] == mac:
                    device['active'] = active
                    state = "activé" if active else "désactivé"
                    logging.info(f"L'abonnement avec MAC {mac} a été {state} manuellement.")

    def parse_webpage(self, url):
        """Parse a webpage to extract subscription information."""
        try:
            response = requests.get(url)
            data = response.text
            self.manage_subscriptions(data)
            logging.info(f"Informations d'abonnement extraites de {url}.")
            messagebox.showinfo("Info", "Les informations d'abonnement ont été extraites et intégrées.")
        except requests.exceptions.RequestException as e:
            logging.error(f"Erreur lors de l'analyse de la page {url}: {e}")
            messagebox.showerror("Erreur", f"Impossible d'analyser la page {url}.")

class IPTVApp:
    def __init__(self, root):
        self.manager = IPTVManager()
        self.root = root
        self.root.title("IPTV Manager")

        self.create_main_widgets()

        # Intégration des abonnements fournis
        self.load_sample_subscriptions()

        # Démarrer le vérificateur de connectivité en arrière-plan
        threading.Thread(target=self.periodic_connectivity_check, daemon=True).start()

    def create_main_widgets(self):
        frame = Frame(self.root)
        frame.pack(fill='both', expand=True)

        Label(frame, text="Liste des Abonnements").grid(row=0, column=0, padx=5, pady=5)

        self.listbox = Listbox(frame, width=50)
        self.listbox.grid(row=1, column=0, rowspan=6, padx=5, pady=5)

        scrollbar = Scrollbar(frame, orient='vertical', command=self.listbox.yview)
        scrollbar.grid(row=1, column=1, rowspan=6, sticky='ns')
        self.listbox.config(yscrollcommand=scrollbar.set)

        # Boutons primaires
        self.load_button = Button(frame, text="Charger Abonnements", command=self.load_subscriptions)
        self.load_button.grid(row=1, column=2, padx=5, pady=5)

        self.view_button = Button(frame, text="Visionner Flux", command=self.view_stream)
        self.view_button.grid(row=2, column=2, padx=5, pady=5)

        self.favorite_button = Button(frame, text="Ajouter aux Favoris", command=self.add_to_favorites)
        self.favorite_button.grid(row=3, column=2, padx=5, pady=5)

        self.history_button = Button(frame, text="Afficher Historique", command=self.show_history)
        self.history_button.grid(row=4, column=2, padx=5, pady=5)

        Label(frame, text="Recherche VOD").grid(row=5, column=0, padx=5, pady=5)

        self.vod_search_entry = Entry(frame)
        self.vod_search_entry.grid(row=6, column=0, padx=5, pady=5)

        self.search_button = Button(frame, text="Rechercher VOD", command=self.search_vod)
        self.search_button.grid(row=6, column=2, padx=5, pady=5)

        # Bouton pour accéder aux réglages
        self.settings_button = Button(frame, text="Réglages", command=self.open_settings)
        self.settings_button.grid(row=7, column=2, padx=5, pady=5)

        # Boutons supplémentaires pour charger depuis le presse-papiers ou une page web
        self.clipboard_button = Button(frame, text="Charger depuis Presse-papier", command=self.manager.load_subscriptions_from_clipboard)
        self.clipboard_button.grid(row=8, column=2, padx=5, pady=5)

        self.webpage_button = Button(frame, text="Analyser Page Web", command=self.open_webpage_input)
        self.webpage_button.grid(row=9, column=2, padx=5, pady=5)

    def open_webpage_input(self):
        webpage_window = Toplevel(self.root)
        webpage_window.title("Analyser Page Web")

        Label(webpage_window, text="Entrez l'URL de la page web:").pack(padx=5, pady=5)
        url_entry = Entry(webpage_window)
        url_entry.pack(padx=5, pady=5)

        Button(webpage_window, text="Analyser", command=lambda: self.manager.parse_webpage(url_entry.get())).pack(padx=5, pady=5)

    def open_settings(self):
        settings_window = Toplevel(self.root)
        settings_window.title("Réglages")

        tab_control = ttk.Notebook(settings_window)

        # Réglages généraux
        general_tab = Frame(tab_control)
        tab_control.add(general_tab, text='Généraux')
        Button(general_tab, text="Changer d'Abonnement", command=self.change_subscription).pack(padx=5, pady=5)

        # Réglages d'image et son
        video_audio_tab = Frame(tab_control)
        tab_control.add(video_audio_tab, text='Vidéo & Son')
        
        Label(video_audio_tab, text="Ratio d'image").pack(padx=5, pady=5)
        ratio_choice = StringVar(video_audio_tab)
        ratio_choice.set("16:9")  # Valeur par défaut
        OptionMenu(video_audio_tab, ratio_choice, "16:9", "4:3", "21:9").pack(padx=5, pady=5)

        Label(video_audio_tab, text="Qualité du Son").pack(padx=5, pady=5)
        sound_choice = StringVar(video_audio_tab)
        sound_choice.set("Standard")  # Valeur par défaut
        OptionMenu(video_audio_tab, sound_choice, "Standard", "Amélioré").pack(padx=5, pady=5)

        # Réglages réseau
        network_tab = Frame(tab_control)
        tab_control.add(network_tab, text='Réseau')

        Label(network_tab, text="Limitation de la Bande Passante").pack(padx=5, pady=5)
        bandwidth_entry = Entry(network_tab)
        bandwidth_entry.pack(padx=5, pady=5)
        Button(network_tab, text="Appliquer", command=lambda: self.apply_network_settings(bandwidth_entry.get())).pack(padx=5, pady=5)

        tab_control.pack(expand=1, fill="both")

    def apply_network_settings(self, bandwidth):
        try:
            bandwidth_value = int(bandwidth)
            logging.info(f"Bande passante ajustée à {bandwidth_value} kbps")
            messagebox.showinfo("Info", f"Bande passante réglée à {bandwidth_value} kbps")
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer une valeur numérique valide.")

    def periodic_connectivity_check(self):
        while True:
            time.sleep(86400 / 3)  # Divise 24 heures par 3 pour avoir trois tests répartis
            self.manager.check_connectivity()
            self.update_listbox()

    def cast_stream(self):
        selected = self.listbox.curselection()
        if selected:
            index = selected[0]
            device = self.manager.channels[index]
            stream_url = device['url']
            device_name = "Default Device"  # Placeholder for actual device name selection
            self.manager.cast_to_device(stream_url, device_name)
        else:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner un abonnement.")

    def load_sample_subscriptions(self):
        sample_data = """
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
        self.manager.manage_subscriptions(sample_data)
        self.update_listbox()

    def update_listbox(self):
        self.listbox.delete(0, END)
        for device in self.manager.channels:
            status = "Actif" if device['active'] else "Inactif"
            color = "red" if not device['active'] else "black"
            self.listbox.insert(END, f"MAC: {device['mac']} - URL: {device['url']} - Statut: {status}")
            self.listbox.itemconfig(END, {'fg': color})

    def load_subscriptions(self):
        file_path = "subscriptions.txt"
        self.manager.load_subscriptions_from_file(file_path)
        self.update_listbox()

    def change_subscription(self):
        selected = self.listbox.curselection()
        if selected:
            index = selected[0]
            mac = self.manager.channels[index]['mac']
            new_url = input("Entrez la nouvelle URL: ")
            self.manager.switch_subscription(mac, new_url)
            messagebox.showinfo("Info", f"Changement effectué pour MAC {mac}.")
        else:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner un abonnement.")

    def view_stream(self):
        selected = self.listbox.curselection()
        if selected:
            index = selected[0]
            device = self.manager.channels[index]
            if not device['active']:
                messagebox.showwarning("Avertissement", "Ce flux est inactif. Veuillez activer l'abonnement avant de visionner.")
                return

            stream_url = device['url']
            if self.manager.test_stream(stream_url, device['mac']):
                player_choice = self.player_choice.get()
                if player_choice == "VLC":
                    instance = vlc.Instance()
                    player = instance.media_player_new()
                    media = instance.media_new(stream_url)
                    player.set_media(media)
                    player.play()
                    self.manager.add_to_history(stream_url)
                    messagebox.showinfo("Info", f"Visionnage du flux {stream_url}.")
                else:
                    player_path = self.get_external_player_path(player_choice)
                    if player_path:
                        self.ma
