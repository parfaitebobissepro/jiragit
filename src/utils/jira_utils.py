import json
from .api import api_call
from src.global_const import GLOBAL_JSON_CONFIG

def jira_api_call(method, endpoint, payload=None):
    """Make an API call to Jira using the provided configuration."""
    url = GLOBAL_JSON_CONFIG["jira"]["url"]
    auth = (GLOBAL_JSON_CONFIG["jira"]["username"], GLOBAL_JSON_CONFIG["jira"]["api_token"])
    headers = {"Content-Type": "application/json"}
    return api_call(url, method, endpoint, auth=auth, headers=headers, payload=payload)

def jira_task_exists(task_number):
    """Check if a Jira task exists."""
    endpoint = f"/rest/api/3/issue/{task_number}"
    response = jira_api_call("GET", endpoint)
    if response.status_code == 200:
        return response.json()
    print(f"La tâche Jira {task_number} est introuvable. Veuillez réessayer.")
    return None

def jira_transition(task_number, status_transition_enum):
    """Transition a Jira task to a new status."""
    if not status_transition_enum.value:
        print(f"État au statut '{status_transition_enum.name}' non valide ou non configuré.")
        return
    print(f"status_transition_enum.value : {status_transition_enum.value}")
    endpoint = f"/rest/api/3/issue/{task_number}/transitions"
    payload = {"transition": {"id": status_transition_enum.value}}
    response = jira_api_call("POST", endpoint, payload)
    if response.status_code == 204:
        print(f"La tâche Jira {task_number} est passée à l'état : {status_transition_enum.name}.")
    else:
        print(f"❌ Erreur lors de la transition de la tâche Jira {task_number} : {response.status_code} {response.text}")

def get_task_infos():
    """Prompt the user for a valid Jira task number and return its type."""
    while True:
        tasks = get_current_sprint_tasks()
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

        task_data = jira_task_exists(task_number)
        if task_data:
            task_type = task_data["fields"]["issuetype"]["name"]
            task_summary = task_data["fields"]["summary"]
            return task_number, task_summary, task_type

def get_current_sprint_tasks():
    """Retrieve all tasks in the current sprint."""
    board_id = GLOBAL_JSON_CONFIG["jira"]["board_id"]
    endpoint = f"/rest/agile/1.0/board/{board_id}/sprint?state=active"
    
    response = jira_api_call("GET", endpoint)
    if response.status_code != 200:
        print(f"❌ Erreur lors de la récupération du sprint actuel : {response.status_code} {response.text}")
        return []

    sprints = response.json().get("values", [])
    if not sprints:
        print("Aucun sprint actif trouvé.")
        return []

    current_sprint_id = sprints[0]["id"]
    endpoint = f"/rest/agile/1.0/sprint/{current_sprint_id}/issue"
    response = jira_api_call("GET", endpoint)
    if response.status_code != 200:
        print(f"❌ Erreur lors de la récupération des tâches du sprint actuel : {response.status_code} {response.text}")
        return []

    issues = response.json().get("issues", [])
    tasks = [(issue["key"], issue["fields"]["summary"], issue["fields"]["issuetype"]["name"]) for issue in issues]
    return tasks

def jira_add_comment(task_number, comment, mr_url=None):
    """Add a comment to a Jira task."""
    endpoint = f"/rest/api/3/issue/{task_number}/comment"

    comment_text = {
                    "text": comment + " ",
                    "type": "text"
                }

    comment_url = {
                    "text":"[Voir la merge request]",
                    "type":"text",
                    "marks":[
                    {
                        "type":"link",
                        "attrs":{
                        "href": mr_url
                        }
                    }
                    ]
                }

    final_content = []

    """Add comment text to final content comment exist."""
    if comment:
        final_content.append(comment_text)

    """Add comment url to final content mr_url exist."""
    if mr_url:
        final_content.append(comment_url)


    payload = {
        "body": {
            "content": [
            {
                "content": final_content,
                "type": "paragraph"
            }
            ],
            "type": "doc",
            "version": 1
        }
    }
    response = jira_api_call("POST", endpoint, payload)
    if response.status_code == 201:
        print(f"Commentaire ajouté à la tâche Jira {task_number}.")
    else:
        print(f"❌ Erreur lors de l'ajout du commentaire à la tâche Jira {task_number} : {response.status_code} {response.text}")

def jira_task_is_in_status(task_number, status):
    """Check if a Jira task is in a specific status."""
    endpoint = f"/rest/api/3/issue/{task_number}"
    response = jira_api_call("GET", endpoint)
    if response.status_code == 200:
        task_data = response.json()
        current_status = task_data["fields"]["status"]["name"]
        return current_status.lower() == str(status).lower()
    print(f"La tâche Jira {task_number} est introuvable. Veuillez réessayer.")
    return False