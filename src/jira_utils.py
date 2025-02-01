import requests
import json
import os

def jira_task_exists(config, task_number):
    """Check if a Jira task exists."""
    jira_url = config["jira_url"]
    auth = (config["jira_username"], config["jira_api_token"])
    url = f"{jira_url}/rest/api/3/issue/{task_number}"
    response = requests.get(url, auth=auth)
    if response.status_code == 200:
        return response.json()
    print(f"La tâche Jira {task_number} est introuvable. Veuillez réessayer.")
    return None

def jira_transition(config, task_number, status):
    """Transition a Jira task to a new status."""
    jira_url = config["jira_url"]
    auth = (config["jira_username"], config["jira_api_token"])
    transition_mapping = {  # Map status names to transition IDs
        "en cours": "2",
        "en revue": "3",
    }
    transition_id = transition_mapping.get(status)
    if not transition_id:
        print(f"État '{status}' non valide ou non configuré.")
        return

    url = f"{jira_url}/rest/api/3/issue/{task_number}/transitions"
    payload = {"transition": {"id": transition_id}}
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, auth=auth, headers=headers)
    if response.status_code == 204:
        print(f"La tâche Jira {task_number} est passée à l'état : {status}.")
    else:
        print(f"❌ Erreur lors de la transition de la tâche Jira {task_number} : {response.status_code} {response.text}")

def get_valid_task_number(config):
    """Prompt the user for a valid Jira task number."""
    while True:
        task_number = input("Entrez le numéro de la tâche Jira : ").strip()
        task_data = jira_task_exists(config, task_number)
        if task_data:
            return task_number, task_data["fields"]["summary"]

def load_config(config_path="../../Tools/devtools/jiragit/config.json"): #path by default
    """Load configuration from an external JSON file."""
    if not os.path.exists(config_path):
        print(f"Fichier de configuration '{config_path}' introuvable.")
        return None
    with open(config_path, "r") as config_file:
        return json.load(config_file)

def jira_add_comment(config, task_number, comment):
    """Add a comment to a Jira task."""
    jira_url = config["jira_url"]
    auth = (config["jira_username"], config["jira_api_token"])
    url = f"{jira_url}/rest/api/3/issue/{task_number}/comment"
    payload = {"body": comment}
    payload = {
        "body": {
            "content": [
            {
                "content": [
                {
                    "text": comment,
                    "type": "text"
                }
                ],
                "type": "paragraph"
            }
            ],
            "type": "doc",
            "version": 1
        }
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, auth=auth, headers=headers)
    if response.status_code == 201:
        print(f"Commentaire ajouté à la tâche Jira {task_number}.")
    else:
        print(f"❌ Erreur lors de l'ajout du commentaire à la tâche Jira {task_number} : {response.status_code} {response.text}")

def jira_task_is_in_status(config, task_number, status):
    """Check if a Jira task is in a specific status."""
    jira_url = config["jira_url"]
    auth = (config["jira_username"], config["jira_api_token"])
    url = f"{jira_url}/rest/api/3/issue/{task_number}"
    response = requests.get(url, auth=auth)
    if response.status_code == 200:
        task_data = response.json()
        current_status = task_data["fields"]["status"]["name"]
        return current_status.lower() == status.lower()
    print(f"La tâche Jira {task_number} est introuvable. Veuillez réessayer.")
    return False