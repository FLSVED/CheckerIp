from tkinter import messagebox, ttk, Listbox, Scrollbar, Canvas, Toplevel, Label, Entry, Menu
import asyncio
from connection_to_server import ServerConnection
from subscriptions import SubscriptionManager

class IPTVApp:
    def __init__(self, root, config_manager):
        self.root = root
        self.config_manager = config_manager
        self.subscription_manager = SubscriptionManager()
        self.create_main_widgets()

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

        add_provider_menu = Menu(frame, tearoff=0)
        add_provider_menu.add_command(label=self.translate("Xtream"), command=self.add_xtream)
        add_provider_menu.add_command(label=self.translate("MAC Portal"), command=self.add_mac_portal)
        add_provider_menu.add_command(label=self.translate("Stalker Portal"), command=self.add_stalker_portal)
        add_provider_menu.add_command(label=self.translate("Fichier Playlist"), command=self.add_playlist_file)
        add_provider_menu.add_command(label=self.translate("Playlist"), command=self.add_playlist)

        add_provider_button = ttk.Menubutton(frame, text=self.translate("Ajouter fournisseur"), menu=add_provider_menu)
        add_provider_button.grid(row=1, column=2, padx=5, pady=5)

        self.view_button = ttk.Button(frame, text=self.translate("PLAY"), command=self.view_stream)
        self.view_button.grid(row=4, column=2, padx=5, pady=5)

        self.favorite_button = ttk.Button(frame, text=self.translate("Ajouter aux Favoris"), command=self.add_to_favorites)
        self.favorite_button.grid(row=5, column=2, padx=5, pady=5)

        self.quit_button = ttk.Button(frame, text=self.translate("Quitter"), command=self.quit_app)
        self.quit_button.grid(row=6, column=2, padx=5, pady=5)

        self.video_canvas = Canvas(frame, width=640, height=360)
        self.video_canvas.grid(row=15, column=0, columnspan=3, padx=5, pady=5)

    def quit_app(self):
        if messagebox.askokcancel("Quit", "Voulez-vous vraiment quitter?"):
            self.root.destroy()

    def add_xtream(self):
        # Implement Xtream addition logic
        pass

    def add_mac_portal(self):
        # Implement MAC Portal addition logic
        pass

    def add_stalker_portal(self):
        # Implement Stalker Portal addition logic
        pass

    def add_playlist_file(self):
        # Implement Playlist File addition logic
        pass

    def add_playlist(self):
        # Implement Playlist addition logic
        pass

    def display_server_content(self, url):
        content_window = Toplevel(self.root)
        content_window.title("Contenu du Serveur")

        connection = ServerConnection(url, self.config_manager.get('mac_address'))

        async def show_content():
            content = await connection.fetch_server_content()
            if content:
                for key, value in content.items():
                    ttk.Label(content_window, text=f"{key}: {value}").pack()
            else:
                ttk.Label(content_window, text="Failed to fetch server content").pack()

        asyncio.run(show_content())

    def translate(self, text):
        # Dummy translation function to illustrate usage.
        return text

    def on_subscription_select(self, event):
        selected = self.listbox.curselection()
        if selected:
            index = selected[0]
            entry = self.listbox.get(index)
            parts = entry.split(" - ")
            url = parts[0].split(": ")[1]
            self.display_server_content(url)

    def update_listbox(self):
        self.listbox.delete(0, 'end')
        for url, devices in self.subscription_manager.subscriptions.items():
            for device in devices:
                if device['active']:
                    self.listbox.insert('end', f"Server: {url} - MAC: {device['mac']}")

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
            parts = entry.split(" - ")
            url = parts[0].split(": ")[1]
            # Implement the logic to add to favorites
            pass
