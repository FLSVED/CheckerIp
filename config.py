import json

__version__ = "1.0.0"

def load_config(file_path='config.json'):
    """
    Load configuration from a JSON file.

    :param file_path: Path to the JSON configuration file
    :return: Configuration data as a dictionary
    :raises FileNotFoundError: If the file does not exist
    :raises json.JSONDecodeError: If the file is not valid JSON
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file {file_path} not found.")
    except json.JSONDecodeError:
        raise json.JSONDecodeError(f"Configuration file {file_path} contains invalid JSON.")
