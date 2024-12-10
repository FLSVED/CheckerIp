from tkinter import Listbox, Button, Scrollbar, END, messagebox, StringVar, Entry, Label, Frame, OptionMenu, Toplevel, Canvas
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

        ttk.Label(frame, text=self.translate("Recherche VOD")).grid(row=6, column=0, padx=5, pady=5)

        self.vod_search_entry = ttk.Entry(frame)
        self.vod_search_entry.grid(row=7, column=0, padx=5, pady=5)

        self.search_button = ttk.Button(frame, text=self.translate("Rechercher VOD"), command=self.search_vod)
        self.search_button.grid(row=7, column=2, padx=5, pady=5)

        self.settings_button = ttk.Button(frame, text=self.translate("Réglages"), command=self.open_settings)
        self.settings_button.grid(row=8, column=2, padx=5, pady=5)

        self.clipboard_button = ttk.Button(frame, text=self.translate("Charger depuis Presse-papier"), command=lambda: asyncio.run(self.load_subscriptions_from_clipboard()))
        self.clipboard_button.grid(row=9, column=2, padx=5, pady=5)

        self.webpage_button = ttk.Button(frame, text=self.translate("Analyser Page Web"), command=self.open_webpage_input)
        self.webpage_button.grid(row=10, column=2, padx=5, pady=5)

        self.load_epg_button = ttk.Button(frame, text=self.translate("Charger EPG"), command=self.load_epg_from_server)
        self.load_epg_button.grid(row=11, column=2, padx=5, pady=5)

        self.paste_text_button = ttk.Button(frame, text=self.translate("Coller Texte"), command=self.open_text_input)
        self.paste_text_button.grid(row=12, column=2, padx=5, pady=5)

        self.m3u_button = ttk.Button(frame, text=self.translate("Charger M3U"), command=self.open_m3u_input)
        self.m3u_button.grid(row=13, column=2, padx=5, pady=5)

        self.filter_var = StringVar(value="Tous")
        ttk.Label(frame, text=self.translate("Filtrer par statut:")).grid(row=14, column=0, padx=5, pady=5)
        self.filter_menu = ttk.OptionMenu(frame, self.filter_var, "Tous", "Actif", "Inactif", command=self.apply_filter)
        self.filter_menu.grid(row=14, column=1, padx=5, pady=5)

        self.video_canvas = Canvas(frame, width=640, height=360)
        self.video_canvas.grid(row=15, column=0, columnspan=3, padx=5, pady=5)

    def translate(self, text):
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

    async def load_subscriptions_from_text(self, text):
        results = await self.subscription_manager.load_subscriptions_from_text(text)
        self.update_listbox()
        if results:
            messagebox.showinfo("Info", "Les abonnements ont été chargés depuis le texte.")
        else:
            messagebox.showerror("Erreur", "Impossible de charger les abonnements depuis le texte.")

    async def load_subscriptions_from_m3u(self, m3u_url):
        results = await self.subscription_manager.load_subscriptions_from_m3u(m3u_url)
        self.update_listbox()
        if results:
            messagebox.showinfo("Info", "Les abonnements ont été chargés depuis le lien M3U.")
        else:
            messagebox.showerror("Erreur", "Impossible de charger les abonnements depuis le lien M3U.")

    def open_text_input(self):
        text_window = Toplevel(self.root)
        text_window.title("Coller Texte")
        ttk.Label(text_window, text="Texte:").pack(padx=10, pady=10)
        text_entry = ttk.Entry(text_window, width=50)
        text_entry.pack(padx=10, pady=10)
        ttk.Button(text_window, text="Charger", command=lambda: asyncio.run(self.load_subscriptions_from_text(text_entry.get()))).pack(padx=10, pady=10)

    def open_m3u_input(self):
        m3u_window = Toplevel(self.root)
        m3u_window.title("Charger M3U")
        ttk.Label(m3u_window, text="URL M3U:").pack(padx=10, pady=10)
        m3u_entry = ttk.Entry(m3u_window, width=50)
        m3u_entry.pack(padx=10, pady=10)
        ttk.Button(m3u_window, text="Charger", command=lambda: asyncio.run(self.load_subscriptions_from_m3u(m3u_entry.get()))).pack(padx=10, pady=10)

    def update_listbox(self):
        self.listbox.delete(0, END)
        for url, devices in self.subscription_manager.subscriptions.items():
            for device in devices:
                status = "Actif" if device['active'] else "Inactif"
                color = "red" if not device['active'] else "black"
                self.listbox.insert(END, f"MAC: {device['mac']} - URL: {url} - Statut: {status}")
                self.listbox.itemconfig(self.listbox.size() - 1, {'fg': color})

    def periodic_connectivity_check(self):
        asyncio.run(self.run_periodic_check())

    async def run_periodic_check(self):
        while True:
            await self.subscription_manager.check_connectivity_async()
            self.update_listbox()
            await asyncio.sleep(60)

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

    def search_vod(self):
        search_query = self.vod_search_entry.get()
        if not search_query:
            messagebox.showwarning("Attention", "Veuillez entrer un terme de recherche.")
            return
        results = self.vod_manager.search_vod(search_query)
        if results:
            self.show_vod_results(results)
        else:
            messagebox.showinfo("Résultats de recherche", "Aucun VOD trouvé.")

    def show_vod_results(self, results):
        result_window = Toplevel(self.root)
        result_window.title("Résultats de recherche VOD")
        listbox = Listbox(result_window, width=50)
        listbox.pack(padx=10, pady=10)
        for result in results:
            listbox.insert(END, result)

    def open_settings(self):
        settings_window = Toplevel(self.root)
        settings_window.title("Réglages")
        ttk.Label(settings_window, text="Réglages").pack(padx=10, pady=10)

    def open_webpage_input(self):
        webpage_window = Toplevel(self.root)
        webpage_window.title("Analyser Page Web")
        ttk.Label(webpage_window, text="URL:").pack(padx=10, pady=10)
        url_entry = ttk.Entry(webpage_window, width=50)
        url_entry.pack(padx=10, pady=10)
        ttk.Button(webpage_window, text="Analyser", command=lambda: self.analyze_webpage(url_entry.get())).pack(padx=10, pady=10)

    def analyze_webpage(self, url):
        messagebox.showinfo("Analyser Page Web", f"Analyzing {url}")

    def load_epg_from_server(self):
        epg_data = self.epg_manager.load_epg()
        if epg_data:
            messagebox.showinfo("EPG", "EPG data loaded from server.")
        else:
            messagebox.showwarning("EPG", "Failed to load EPG data.")

    def apply_filter(self, selected_filter):
        messagebox.showinfo("Filtre", f"Filtrage appliqué: {selected_filter}")
