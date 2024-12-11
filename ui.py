from tkinter import Listbox, Scrollbar, END, messagebox, StringVar, Canvas, Toplevel, filedialog, Entry, Label, Button
from tkinter import ttk
import threading
import logging
import pyperclip
import asyncio
import time
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

        ttk.Label(frame, text=self.translate("Abonnements Actifs")).grid(row=0, column=0, padx=5, pady=5)

        self.listbox = Listbox(frame, width=50)
        self.listbox.grid(row=1, column=0, rowspan=6, padx=5, pady=5)
        self.listbox.bind('<<ListboxSelect>>', self.on_subscription_select)

        scrollbar = Scrollbar(frame, orient='vertical', command=self.listbox.yview)
        scrollbar.grid(row=1, column=1, rowspan=6, sticky='ns')
        self.listbox.config(yscrollcommand=scrollbar.set)

        self.add_from_file_button = ttk.Button(frame, text=self.translate("Ajouter depuis un fichier"), command=self.load_from_file)
        self.add_from_file_button.grid(row=1, column=2, padx=5, pady=5)

        self.add_manual_button = ttk.Button(frame, text=self.translate("Ajouter manuellement"), command=self.add_manual_subscription)
        self.add_manual_button.grid(row=2, column=2, padx=5, pady=5)

        self.add_from_web_button = ttk.Button(frame, text=self.translate("Ajouter depuis un lien web"), command=self.add_from_web)
        self.add_from_web_button.grid(row=3, column=2, padx=5, pady=5)

        self.view_button = ttk.Button(frame, text=self.translate("PLAY"), command=self.view_stream)
        self.view_button.grid(row=4, column=2, padx=5, pady=5)

        self.favorite_button = ttk.Button(frame, text=self.translate("Ajouter aux Favoris"), command=self.add_to_favorites)
        self.favorite_button.grid(row=5, column=2, padx=5, pady=5)

        self.video_canvas = Canvas(frame, width=640, height=360)
        self.video_canvas.grid(row=15, column=0, columnspan=3, padx=5, pady=5)

    def load_from_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = file.read()
            asyncio.run(self.subscription_manager.load_subscriptions_from_text(data))
            self.update_listbox()

    def add_manual_subscription(self):
        manual_window = Toplevel(self.root)
        manual_window.title("Ajouter un Abonnement Manuel")

        Label(manual_window, text="URL du Serveur:").grid(row=0, column=0, padx=5, pady=5)
        url_entry = Entry(manual_window, width=50)
        url_entry.grid(row=0, column=1, padx=5, pady=5)

        Label(manual_window, text="Adresse MAC:").grid(row=1, column=0, padx=5, pady=5)
        mac_entry = Entry(manual_window, width=50)
        mac_entry.grid(row=1, column=1, padx=5, pady=5)

        def add_subscription():
            url = url_entry.get()
            mac = mac_entry.get()
            asyncio.run(self.subscription_manager.add_subscription_async(url, mac))
            self.update_listbox()
            manual_window.destroy()

        add_button = ttk.Button(manual_window, text="Ajouter", command=add_subscription)
        add_button.grid(row=2, column=1, padx=5, pady=5)

    def add_from_web(self):
        web_window = Toplevel(self.root)
        web_window.title("Ajouter un Abonnement depuis un Lien Web")

        Label(web_window, text="URL du Serveur:").grid(row=0, column=0, padx=5, pady=5)
        url_entry = Entry(web_window, width=50)
        url_entry.grid(row=0, column=1, padx=5, pady=5)

        def add_subscription():
            url = url_entry.get()
            asyncio.run(self.subscription_manager.load_subscriptions_from_m3u(url))
            self.update_listbox()
            web_window.destroy()

        add_button = ttk.Button(web_window, text="Ajouter", command=add_subscription)
        add_button.grid(row=1, column=1, padx=5, pady=5)

    def update_listbox(self):
        self.listbox.delete(0, END)
        for url, devices in self.subscription_manager.subscriptions.items():
            for device in devices:
                if device['active']:
                    self.listbox.insert(END, f"Server: {url} - MAC: {device['mac']}")

    def on_subscription_select(self, event):
        selected = self.listbox.curselection()
        if selected:
            index = selected[0]
            entry = self.listbox.get(index)
            parts = entry.split(" - ")
            url = parts[0].split(": ")[1]
            self.display_server_content(url)

    def display_server_content(self, url):
        content_window = Toplevel(self.root)
        content_window.title("Contenu du Serveur")

        # Implement the logic to fetch and display server content
        # For example, you could display TV channels, VOD, EPG, etc.
        Label(content_window, text=f"Content from {url}").pack()

    def view_stream(self):
        selected = self.listbox.curselection()
        if selected:
            index = selected[0]
            entry = self.listbox.get(index)
            parts = entry.split(" - ")
            url = parts[0].split(": ")[1]
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

    def translate(self, text):
        return text

    async def load_subscriptions(self):
        results = await self.subscription_manager.manage_subscriptions_async("")
        self.update_listbox()
        for line in results:
            logging.info(line)

    def periodic_connectivity_check(self):
        while True:
            asyncio.run(self.subscription_manager.check_connectivity_async())
            time.sleep(60)  # Pause for 60 seconds between checks
