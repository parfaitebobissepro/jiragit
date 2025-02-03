import os
import json
import sys

def load_config(): #path by default
    """Load configuration from an external JSON file."""
    jiragit_home = os.getenv('JIRAGIT_HOME')
    if jiragit_home is None:
        print("Erreur: la variable d'environnement 'JIRAGIT_HOME' n'est pas définie.")
        sys.exit(1)
    config_path = os.path.join(jiragit_home, "config.json")
    if not os.path.exists(config_path):
        print(f"Fichier de configuration '{config_path}' introuvable.")
        sys.exit(1)
    with open(config_path, "r") as config_file:
        return json.load(config_file)
