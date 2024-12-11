def display_server_content(self, url):
    content_window = Toplevel(self.root)
    content_window.title("Contenu du Serveur")

    connection = ServerConnection(url, self.config_manager.get('mac_address'))

    async def show_content():
        content = await connection.fetch_server_content()
        if content:
            for key, value in content.items():
                Label(content_window, text=f"{key}: {value}").pack()
        else:
            Label(content_window, text="Failed to fetch server content").pack()

    asyncio.run(show_content())
