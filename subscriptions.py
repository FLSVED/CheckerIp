class SubscriptionManager:
    def __init__(self):
        self.subscriptions = {}
        self.connectivity_failures = {}
        self.load_default_subscriptions()

    def load_default_subscriptions(self):
        """Load the default subscriptions at startup."""
        urls, devices = self.parse_data(DEFAULT_SUBSCRIPTIONS)
        if not urls or not devices:
            logging.info("No default subscriptions found.")
            return  # Proceed without default subscriptions
        for url in urls:
            for device in devices:
                asyncio.run(self.add_subscription_async(url, device['mac']))
