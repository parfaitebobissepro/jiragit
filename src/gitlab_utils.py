import requests
import json
import subprocess
import re
import os

def load_config():
    """Charge la configuration depuis config.json"""
    config_path = "config.json"
    if not os.path.exists(config_path):
        print(f"❌ Fichier de configuration '{config_path}' introuvable.")
        return None
    with open(config_path, "r") as config_file:
        return json.load(config_file)

def get_gitlab_token(config, project_name):
    """Récupère le bon token GitLab : d'abord gitlab_token, sinon cherche dans gitlab_tokens."""
    if "gitlab_token" in config and config["gitlab_token"]:
        print("✅ Utilisation du gitlab_token principal.")
        return config["gitlab_token"]

    # Rechercher dans gitlab_tokens si un mapping existe pour le projet
    if "gitlab_tokens" in config:
        for token_mapping in config["gitlab_tokens"]:
            if project_name in token_mapping:
                print(f"✅ Token trouvé pour le projet {project_name}.")
                return token_mapping[project_name]

    print(f"❌ Aucun token trouvé pour le projet {project_name}. Vérifiez config.json.")
    return None

def get_project_id(config, token):
    """Récupère dynamiquement l'ID du projet GitLab en fonction du dépôt local."""
    gitlab_url = config["gitlab_url"].rstrip("/")

    # Récupérer l'URL du dépôt Git local
    remote_url = run_command("git remote get-url origin").strip()

    if not remote_url:
        print("❌ Impossible de récupérer l'URL du dépôt distant.")
        return None, None

    # Extraire le nom du projet GitLab
    match = re.search(r'gitlab\.com[:/](.+)\.git', remote_url)
    if not match:
        print("❌ Impossible d'extraire le chemin du projet depuis l'URL :", remote_url)
        return None, None

    project_path = match.group(1)
    encoded_path = project_path.replace("/", "%2F")  # Encodage URL pour GitLab API

    # Récupérer l'ID du projet via l'API GitLab
    url = f"{gitlab_url}/api/v4/projects/{encoded_path}"
    headers = {"PRIVATE-TOKEN": token}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        project_id = response.json()["id"]
        print(f"✅ Projet GitLab détecté : {project_path} (ID: {project_id})")
        return project_id, project_path
    else:
        print("❌ Erreur lors de la récupération de l'ID du projet :", response.text)
        return None, None

def create_merge_request(config, branch_name, title):
    """Crée une Merge Request sur GitLab en utilisant l'API REST."""
    # Récupérer l'ID du projet et son nom
    project_id, project_name = get_project_id(config, get_gitlab_token(config, ""))
    
    if not project_id or not project_name:
        print("❌ Impossible de récupérer l'ID du projet. Annulation de la MR.")
        return
    
    # Trouver le bon token
    token = get_gitlab_token(config, project_name)
    if not token:
        print("❌ Aucun token valide trouvé. Impossible de créer la MR.")
        return

    gitlab_url = config["gitlab_url"].rstrip("/")
    url = f"{gitlab_url}/api/v4/projects/{project_id}/merge_requests"
    headers = {"PRIVATE-TOKEN": token, "Content-Type": "application/json"}
    description = input("Entrez la description de la merge request : ").strip()
    
    data = {
        "source_branch": branch_name,
        "target_branch": "develop",
        "title": title,
        "description": description,
        "assignee_id": None
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        print("✅ Merge Request créée avec succès :", response.json()["web_url"])
    else:
        print("❌ Erreur lors de la création de la Merge Request :", response.text)

def run_command(command):
    """Exécute une commande shell et retourne sa sortie."""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'exécution de la commande : {command}\n{e.stderr}")
        return None
