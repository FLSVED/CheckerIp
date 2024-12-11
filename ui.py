from tkinter import messagebox, ttk, Listbox, Scrollbar, Canvas, Toplevel
import asyncio
from connection_to_server import ServerConnection

class IPTVApp:
    def __init__(self, root, config_manager):
        self.root = root
        self.config_manager = config_manager
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

        self.quit_button = ttk.Button(frame, text=self.translate("Quitter"), command=self.quit_app)
        self.quit_button.grid(row=6, column=2, padx=5, pady=5)

        self.video_canvas = Canvas(frame, width=640, height=360)
        self.video_canvas.grid(row=15, column=0, columnspan=3, padx=5, pady=5)

    def quit_app(self):
        if messagebox.askokcancel("Quit", "Voulez-vous vraiment quitter?"):
            self.root.destroy()

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
        # Placeholder for subscription select event handler.
        pass

    def load_from_file(self):
        # Placeholder for loading from file.
        pass

    def add_manual_subscription(self):
        # Placeholder for adding manual subscription.
        pass

    def add_from_web(self):
        # Placeholder for adding from web.
        pass

    def view_stream(self):
        # Placeholder for viewing stream.
        pass

    def add_to_favorites(self):
        # Placeholder for adding to favorites.
        pass
