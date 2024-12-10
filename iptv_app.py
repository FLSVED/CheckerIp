from tkinter import Frame, Label

class IPTVApp(Frame):
    def __init__(self, master, config_manager):
        super().__init__(master)
        self.config_manager = config_manager
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.label = Label(self, text="Welcome to IPTV Manager")
        self.label.pack()
