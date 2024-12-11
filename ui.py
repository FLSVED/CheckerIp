from tkinter import Listbox, Scrollbar, END, messagebox, StringVar, Canvas, Toplevel, filedialog
from tkinter import ttk
import threading
import logging
import pyperclip
import asyncio
from subscriptions import SubscriptionManager
from vod import VodManager
from epg import EpgManager
import vlc

__version__ = "2.0.0"

class IPTVApp:
    def __init__(self, root, config_manager):
        self.root = root
        self.root.title("IPTV Manager")
        self.config_manager = config_manager
        self.server_url = config_manager.get('server_url')
        self.mac_address = config_manager.get('mac_address')
        
        self.subscription_manager = SubscriptionManager()
        self.vod_manager = VodManager()
        self.epg_manager = EpgManager()

        self.player_choice = StringVar(value="VLC")
        self.external_player_paths = config_manager.get('external_players')

        self.favorites = []

        self.create_main_widgets()
        threading.Thread(target=self.periodic_connectivity_check, daemon=True).start()

    def create_main_widgets(self):
        style = ttk.Style()
        style.theme_use('clam')

        frame = ttk.Frame(self.root)
        frame.pack(fill='both', expand=True)

        ttk.Label(frame, text=self.translate("Liste des Abonnements")).grid(row=0, column=0, padx=5, pady=5)

        self.listbox = Listbox(frame, width=50)
        self.listbox.grid(row=1, column=0, rowspan=6, padx=5, pady=5)

        scrollbar = Scrollbar(frame, orient='vertical', command=self.listbox.yview)
        scrollbar.grid(row=1, column=1, rowspan=6, sticky='ns')
        self.listbox.config(yscrollcommand=scrollbar.set)

        self.load_button = ttk.Button(frame, text=self.translate("Charger Abonnements"), command=lambda: asyncio.run(self.load_subscriptions()))
        self.load_button.grid(row=1, column=2, padx=5, pady=5)

        self.view_button = ttk.Button(frame, text=self.translate("Visionner Flux"), command=self.view_stream)
        self.view_button.grid(row=2, column=2, padx=5, pady=5)

        self.favorite_button = ttk.Button(frame, text=self.translate("Ajouter aux Favoris"), command=self.add_to_favorites)
        self.favorite_button.grid(row=3, column=2, padx=5, pady=5)

        self.remove_favorite_button = ttk.Button(frame, text=self.translate("Supprimer des Favoris"), command=self.remove_from_favorites)
        self.remove_favorite_button.grid(row=4, column=2, padx=5, pady=5)

        self.history_button = ttk.Button(frame, text=self.translate("Afficher Historique"), command=self.show_history)
        self.history_button.grid(row=5, column=2, padx=5, pady=5)

        self.add_from_file_button = ttk.Button(frame, text=self.translate("Ajouter depuis"), command=self.load_from_file)
        self.add_from_file_button.grid(row=6, column=2, padx=5, pady=5)

        self.video_canvas = Canvas(frame, width=640, height=360)
        self.video_canvas.grid(row=15, column=0, columnspan=3, padx=5, pady=5)

    def load_from_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'r') as file:
                data = file.read()
            asyncio.run(self.subscription_manager.load_subscriptions_from_text(data))

    def view_stream(self):
        selected = self.listbox.curselection()
        if selected:
            index = selected[0]
            entry = self.listbox.get(index)
            parts = entry.split(" - ")
            url = parts[1].split(": ")[1]
            self.play_video(url)

    def play_video(self, url):
        instance = vlc.Instance()
        player = instance.media_player_new()
        media = instance.media_new(url)
        player.set_media(media)
        player.set_xwindow(self.video_canvas.winfo_id())
        player.play()

    def add_to_favorites(self):
        selected = self.listbox.curselection()
        if selected:
            index = selected[0]
            entry = self.listbox.get(index)
            if entry not in self.favorites:
                self.favorites.append(entry)
                messagebox.showinfo("Favoris", f"{entry} a été ajouté aux favoris.")
            else:
                messagebox.showinfo("Favoris", f"{entry} est déjà dans les favoris.")

    def remove_from_favorites(self):
        selected = self.listbox.curselection()
        if selected:
            index = selected[0]
            entry = self.listbox.get(index)
            if entry in self.favorites:
                self.favorites.remove(entry)
                messagebox.showinfo("Favoris", f"{entry} a été retiré des favoris.")
            else:
                messagebox.showinfo("Favoris", f"{entry} n'est pas dans les favoris.")

    def show_history(self):
        messagebox.showinfo("Historique", "Historique affiché.")

    def translate(self, text):
        return text

    async def load_subscriptions(self):
        report, _ = await self.subscription_manager.manage_subscriptions_async("")
        self.update_listbox()
        for line in report:
            logging.info(line)

    # Additional methods for periodic connectivity check, updating listbox, etc.
