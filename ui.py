from tkinter import Listbox, Button, Scrollbar, END, messagebox, StringVar, Entry, Label, Frame, OptionMenu
import threading
import logging
import pyperclip
import asyncio
from subscriptions import SubscriptionManager
from streaming import StreamManager
from vod import VodManager
from epg import EpgManager

__version__ = "1.0.0"

class IPTVApp:
    def __init__(self, root, config):
        self.root = root
        self.root.title("IPTV Manager")
        self.config = config
        
        self.subscription_manager = SubscriptionManager()
        self.stream_manager = StreamManager()
        self.vod_manager = VodManager()
        self.epg_manager = EpgManager()

        self.player_choice = StringVar(value="VLC")
        self.external_player_paths = self.config['external_players']

        self.create_main_widgets()
        threading.Thread(target=self.periodic_connectivity_check, daemon=True).start()

    def create_main_widgets(self):
        frame = Frame(self.root)
        frame.pack(fill='both', expand=True)

        Label(frame, text=self.translate("Liste des Abonnements")).grid(row=0, column=0, padx=5, pady=5)

        self.listbox = Listbox(frame, width=50)
        self.listbox.grid(row=1, column=0, rowspan=6, padx=5, pady=5)

        scrollbar = Scrollbar(frame, orient='vertical', command=self.listbox.yview)
        scrollbar.grid(row=1, column=1, rowspan=6, sticky='ns')
        self.listbox.config(yscrollcommand=scrollbar.set)

        self.load_button = Button(frame, text=self.translate("Charger Abonnements"), command=lambda: asyncio.run(self.load_subscriptions()))
        self.load_button.grid(row=1, column=2, padx=5, pady=5)

        self.view_button = Button(frame, text=self.translate("Visionner Flux"), command=self.view_stream)
        self.view_button.grid(row=2, column=2, padx=5, pady=5)

        self.favorite_button = Button(frame, text=self.translate("Ajouter aux Favoris"), command=self.add_to_favorites)
        self.favorite_button.grid(row=3, column=2, padx=5, pady=5)

        self.remove_favorite_button = Button(frame, text=self.translate("Supprimer des Favoris"), command=self.remove_from_favorites)
        self.remove_favorite_button.grid(row=4, column=2, padx=5, pady=5)

        self.history_button = Button(frame, text=self.translate("Afficher Historique"), command=self.show_history)
        self.history_button.grid(row=5, column=2, padx=5, pady=5)

        Label(frame, text=self.translate("Recherche VOD")).grid(row=6, column=0, padx=5, pady=5)

        self.vod_search_entry = Entry(frame)
        self.vod_search_entry.grid(row=7, column=0, padx=5, pady=5)

        self.search_button = Button(frame, text=self.translate("Rechercher VOD"), command=self.search_vod)
        self.search_button.grid(row=7, column=2, padx=5, pady=5)

        self.settings_button = Button(frame, text=self.translate("Réglages"), command=self.open_settings)
        self.settings_button.grid(row=8, column=2, padx=5, pady=5)

        self.clipboard_button = Button(frame, text=self.translate("Charger depuis Presse-papier"), command=lambda: asyncio.run(self.load_subscriptions_from_clipboard()))
        self.clipboard_button.grid(row=9, column=2, padx=5, pady=5)

        self.webpage_button = Button(frame, text=self.translate("Analyser Page Web"), command=self.open_webpage_input)
        self.webpage_button.grid(row=10, column=2, padx=5, pady=5)

        self.load_epg_button = Button(frame, text=self.translate("Charger EPG"), command=self.load_epg_from_server)
        self.load_epg_button.grid(row=11, column=2, padx=5, pady=5)

        # Options de filtre et de tri
        self.filter_var = StringVar(value="Tous")
        Label(frame, text=self.translate("Filtrer par statut:")).grid(row=12, column=0, padx=5, pady=5)
        self.filter_menu = OptionMenu(frame, self.filter_var, "Tous", "Actif", "Inactif", command=self.apply_filter)
        self.filter_menu.grid(row=12, column=1, padx=5, pady=5)

    def translate(self, text):
        # Placeholder for internationalization logic; replace with actual i18n solution
        return text

    async def load_subscriptions(self):
        report, _ = await self.subscription_manager.manage_subscriptions_async("")
        self.update_listbox()
        for line in report:
            logging.info(line)

    async def load_subscriptions_from_clipboard(self):
        try:
            data = pyperclip.paste()
            report, _ = await self.subscription_manager.manage_subscriptions_async(data)
            self.update_listbox()
            for line in report:
                logging.info(line)
            messagebox.showinfo("Info", "Les abonnements ont été chargés depuis le presse-papiers.")
        except Exception as e:
            logging.error(f"Erreur lors du chargement du presse-papiers: {e}")
            messagebox.showerror("Erreur", "Impossible de charger les abonnements depuis le presse-papiers.")

    def update_listbox(self):
        self.listbox.delete(0, END)
        for url, devices in self.subscription_manager.subscriptions.items():
            for device in devices:
                status = "Actif" if device['active'] else "Inactif"
                color = "red" if not device['active'] else "black"
                self.listbox.insert(END, f"MAC: {device['mac']} - URL: {url} - Statut: {status}")
                self.listbox.itemconfig(self.listbox.size() - 1, {'fg': color})

    def periodic_connectivity_check(self):
        while True:
            asyncio.run(self.subscription_manager.check_connectivity_async())
            self.update_listbox()

    def view_stream(self):
        selected = self.listbox.curselection()
        if selected:
            index = selected[0]
            entry = self.listbox.get(index)
            # Extract MAC and URL from the selected entry
            parts = entry.split(" - ")
            mac = parts[0].split(": ")[1]
            url = parts[1].split(": ")[1]
            # Here you would integrate with the StreamManager to play the stream
            # Example: self.stream_manager.play_with_vlc(url)
            messagebox.showinfo("Stream Info", f"Playing stream for MAC: {mac} on URL: {url}")

    def add_to_favorites(self):
        selected = self.listbox.curselection()
        if selected:
            index = selected[0]
            entry = self.listbox.get(index)
            # Add the selected entry to favorites (implement your favorite logic here)
            # Example: self.favorites.append(entry)
            messagebox.showinfo("Favoris", f"Ajouté aux favoris: {entry}")

    def remove_from_favorites(self):
        # Implement the logic to remove from favorites
        pass

    def show_history(self):
        # Implement the logic to show history
        pass

    def search_vod(self):
        # Implement the logic to search VOD
        pass

    def open_settings(self):
        # Implement the logic to open settings
        pass

    def apply_filter(self, filter_value):
        # Implement the logic to apply filter
        pass
