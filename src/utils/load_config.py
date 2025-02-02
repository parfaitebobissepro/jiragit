import os
import json

def load_config(config_path=None): #path by default
    """Load configuration from an external JSON file."""
    if config_path is None:
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config.json")
    if not os.path.exists(config_path):
        print(f"Fichier de configuration '{config_path}' introuvable.")
        return None
    with open(config_path, "r") as config_file:
        return json.load(config_file)