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
    transition_mapping = config.get("jira_workflow", {})
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

def get_task_infos(config):
    """Prompt the user for a valid Jira task number and return its type."""
    while True:
        tasks = get_current_sprint_tasks(config)
        if not tasks:
            print("Aucune tâche trouvée dans le sprint actuel.")
            continue

        """Filter tasks to only include 'Tâche' and 'Bug'."""
        filtered_tasks = [task for task in tasks if task[2] in ["Tâche", "Bug"]]

        if not filtered_tasks:
            print("Aucune tâche ou bug trouvé dans le sprint actuel.")
            continue

        """Print filtered tasks in the current sprint with numbers."""
        print("\n--- Tâches et Bugs du Sprint Actuel ---")
        for idx, task in enumerate(filtered_tasks, start=1):
            print(f"{idx}. {task[0]} - {task[1]} ({task[2]})")

        print(f"{len(filtered_tasks) + 1}. Entrer manuellement le numéro de la tâche")

        try:
            choice = int(input("Sélectionnez le numéro de la tâche ou entrez le numéro de la tâche Jira : ").strip())
            if choice == len(filtered_tasks) + 1:
                task_number = input("Entrez le numéro de la tâche Jira : ").strip()
            else:
                task_number = filtered_tasks[choice - 1][0]
        except (ValueError, IndexError):
            print("Choix invalide. Veuillez réessayer.")
            continue

        task_data = jira_task_exists(config, task_number)
        if task_data:
            task_type = task_data["fields"]["issuetype"]["name"]
            task_summary = task_data["fields"]["summary"]
            return task_number, task_summary, task_type

def get_current_sprint_tasks(config):
    """Retrieve all tasks in the current sprint."""
    jira_url = config["jira_url"]
    auth = (config["jira_username"], config["jira_api_token"])
    board_id = config["jira_board_id"]
    url = f"{jira_url}/rest/agile/1.0/board/{board_id}/sprint?state=active"
    
    response = requests.get(url, auth=auth)
    if response.status_code != 200:
        print(f"❌ Erreur lors de la récupération du sprint actuel : {response.status_code} {response.text}")
        return []

    sprints = response.json().get("values", [])
    if not sprints:
        print("Aucun sprint actif trouvé.")
        return []

    current_sprint_id = sprints[0]["id"]
    url = f"{jira_url}/rest/agile/1.0/sprint/{current_sprint_id}/issue"
    response = requests.get(url, auth=auth)
    if response.status_code != 200:
        print(f"❌ Erreur lors de la récupération des tâches du sprint actuel : {response.status_code} {response.text}")
        return []

    issues = response.json().get("issues", [])
    tasks = [(issue["key"], issue["fields"]["summary"], issue["fields"]["issuetype"]["name"]) for issue in issues]
    return tasks

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