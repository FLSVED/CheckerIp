import json
import os

__version__ = "1.0.0"

def load_config(file_path=None):
    if file_path is None:
        # Use the absolute path to ensure the file can be found
        file_path = os.path.join(os.path.dirname(__file__), 'config.json')

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Configuration file {file_path} not found.")

    with open(file_path, 'r') as f:
        return json.load(f)
