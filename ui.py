from tkinter import messagebox

class IPTVApp:
    # Existing code...

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

    # Existing code...
