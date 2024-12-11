import yaml
import os

class ConfigManager:

    def __init__(self, config_file='config.yaml'):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        if not os.path.isfile(self.config_file):
            raise FileNotFoundError(f"Configuration file {self.config_file} not found.")
        try:
            with open(self.config_file, 'r') as file:
                return yaml.safe_load(file)
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing configuration file: {e}")

    def get(self, key, default=None):
        return self.config.get(key, default)

    def update(self, key, value):
        self.config[key] = value
        with open(self.config_file, 'w') as file:
            yaml.safe_dump(self.config, file)
