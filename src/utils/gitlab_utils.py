import json
import re
import os
from .run_command import run_command
from .api import api_call
from src.global_const import GLOBAL_JSON_CONFIG, REMOTE_REPO_NAME

def get_gitlab_token(project_name):
    """Récupère le bon token GitLab : d'abord gitlab_token, sinon cherche dans gitlab_tokens."""
    if "token" in GLOBAL_JSON_CONFIG["gitlab"]:
        print("✅ Utilisation du gitlab_token principal.")
        return GLOBAL_JSON_CONFIG["gitlab"]["token"]

    # Rechercher dans gitlab_tokens si un mapping existe pour le projet
    if "gitlab" in GLOBAL_JSON_CONFIG:
        for token_mapping in GLOBAL_JSON_CONFIG["gitlab"]["tokens"]:
            if project_name in token_mapping:
                print(f"✅ Token trouvé pour le projet {project_name}.")
                return token_mapping[project_name]

    print(f"❌ Aucun token trouvé pour le projet {project_name}. Vérifiez config.json.")
    return None

def get_remote_url():
    """Récupère l'URL du dépôt Git local."""
    remote_url = run_command(f"git remote get-url {REMOTE_REPO_NAME}").strip()
    if not remote_url:
        print("❌ Impossible de récupérer l'URL du dépôt distant.")
        return None
    return remote_url

def extract_project_path(remote_url):
    """Extrait le chemin du projet GitLab depuis l'URL du dépôt Git."""
    match = re.search(r'gitlab\.com[:/](.+)\.git', remote_url)
    if not match:
        print("❌ Impossible d'extraire le chemin du projet depuis l'URL :", remote_url)
        return None
    return match.group(1)

def get_project_id(token):
    """Récupère dynamiquement l'ID du projet GitLab en fonction du dépôt local."""
    gitlab_url = GLOBAL_JSON_CONFIG["gitlab"]["url"].rstrip("/")

    # Récupérer l'URL du dépôt Git local
    remote_url = get_remote_url()
    if not remote_url:
        return None, None

    # Extraire le nom du projet GitLab
    project_path = extract_project_path(remote_url)
    if not project_path:
        return None, None

    encoded_path = project_path.replace("/", "%2F")  # Encodage URL pour GitLab API

    # Récupérer l'ID du projet via l'API GitLab
    url = f"{gitlab_url}/api/v4/projects/{encoded_path}"
    headers = {"PRIVATE-TOKEN": token}

    response = api_call(url, "GET", "", headers=headers)

    if response:
        project_id = response.json()["id"]
        print(f"✅ Projet GitLab détecté : {project_path} (ID: {project_id})")
        return project_id, project_path
    else:
        return None, None

def create_merge_request(branch_name, title):
    """Crée une Merge Request sur GitLab en utilisant l'API REST."""
    # Récupérer l'ID du projet et son nom
    project_id, project_name = get_project_id(get_gitlab_token(""))
    
    if not project_id or not project_name:
        print("❌ Impossible de récupérer l'ID du projet. Annulation de la MR.")
        return
    
    # Trouver le bon token
    token = get_gitlab_token(project_name)
    if not token:
        print("❌ Aucun token valide trouvé. Impossible de créer la MR.")
        return

    gitlab_url = GLOBAL_JSON_CONFIG["gitlab"]["url"].rstrip("/")
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
    
    response = api_call(url, "POST", "", headers=headers, payload=data)
    
    if response:
        print("✅ Merge Request créée avec succès :", response.json()["web_url"])
    else:
        print("❌ Erreur lors de la création de la Merge Request.")
