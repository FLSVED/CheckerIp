python
__version__ = "1.0.0"

class VodManager:
    def __init__(self):
        self.vod_list = []

    def load_vod(self, vod_data):
        self.vod_list = vod_data.splitlines()

    def search_vod(self, query):
        return [vod for vod in self.vod_list if query.lower() in vod.lower()]
