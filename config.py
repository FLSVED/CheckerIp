import json
import os

__version__ = "1.0.0"

def load_config(file_path=None):
    if file_path is None:
        # Use absolute path for the config file
        file_path = os.path.join(os.path.dirname(__file__), 'config.json')

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Configuration file {file_path} not found.")

    with open(file_path, 'r') as f:
        return json.load(f)
