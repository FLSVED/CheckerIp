import json

class IPTVApp:
    def __init__(self, root, config_manager):
        self.root = root
        self.config_manager = config_manager
        self.subscription_manager = SubscriptionManager()
        self.load_stored_subscription()
        self.create_main_widgets()

    def create_main_widgets(self):
        # Existing code...
        self.auto_connect()

    def auto_connect(self):
        # Automatically connect using stored credentials if available
        if hasattr(self, 'stored_subscription'):
            url, mac = self.stored_subscription
            connection = ServerConnection(url, mac)
            asyncio.run(connection.connect())

    def store_subscription(self, url, mac):
        # Store the subscription credentials in a JSON file or any secure storage
        with open('subscription.json', 'w') as f:
            json.dump({'url': url, 'mac': mac}, f)

    def load_stored_subscription(self):
        # Load the stored subscription credentials if available
        try:
            with open('subscription.json', 'r') as f:
                data = json.load(f)
                self.stored_subscription = (data['url'], data['mac'])
        except FileNotFoundError:
            self.stored_subscription = None

    def add_manual_subscription(self, mode):
        manual_window = Toplevel(self.root)
        manual_window.title(f"Ajouter un Abonnement {mode}")

        Label(manual_window, text="URL du Serveur:").grid(row=0, column=0, padx=5, pady=5)
        url_entry = Entry(manual_window, width=50)
        url_entry.grid(row=0, column=1, padx=5, pady=5)

        if mode != "Xtream":
            Label(manual_window, text="Adresse MAC:").grid(row=1, column=0, padx=5, pady=5)
            mac_entry = Entry(manual_window, width=50)
            mac_entry.grid(row=1, column=1, padx=5, pady=5)
        else:
            mac_entry = None

        def add_subscription():
            url = url_entry.get()
            mac = mac_entry.get() if mac_entry else None
            self.store_subscription(url, mac)  # Store subscription for automatic connection
            asyncio.run(self.subscription_manager.add_subscription_async(url, mac))
            self.update_listbox()
            manual_window.destroy()

        add_button = ttk.Button(manual_window, text="Ajouter", command=add_subscription)
        add_button.grid(row=2, column=1, padx=5, pady=5)

    # Existing methods...
