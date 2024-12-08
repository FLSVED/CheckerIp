import json
from tkinter import Tk
from ui import IPTVApp
from config import load_config

def main():
    config = load_config()
    root = Tk()
    app = IPTVApp(root, config)
    root.mainloop()

if __name__ == "__main__":
    main()
