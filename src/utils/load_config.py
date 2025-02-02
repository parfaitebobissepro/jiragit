import os
import json

def load_config(config_path="../../Tools/devtools/jiragit/config.json"): #path by default
    """Load configuration from an external JSON file."""
    if not os.path.exists(config_path):
        print(f"Fichier de configuration '{config_path}' introuvable.")
        return None
    with open(config_path, "r") as config_file:
        return json.load(config_file)