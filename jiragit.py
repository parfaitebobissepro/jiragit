import subprocess
import json
import requests
import os
import unicodedata


def load_config():
    """Load configuration from an external JSON file."""
    #TODO:extraire le path
    config_path = "../../Tools/devtools/jiragit/config.json"
    if not os.path.exists(config_path):
        print(f"Fichier de configuration '{config_path}' introuvable.")
        return None
    with open(config_path, "r") as config_file:
        return json.load(config_file)


def run_command(command):
    """Run a shell command and return its output."""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution de la commande : {command}\n{e.stderr}")
        return None


def remove_accents(input_str):
    """Remove accents from a string."""
    normalized_str = unicodedata.normalize("NFD", input_str)
    return "".join(c for c in normalized_str if unicodedata.category(c) != "Mn")


def generate_branch_name(task_code, title):
    """Generate a branch name based on the task code and title."""
    sanitized_title = remove_accents("_".join(title.lower().split()))
    branch_base = f"feature/{task_code}_{sanitized_title}"

    # If the branch name exceeds 80 characters, limit the title
    if len(branch_base) > 80:
        words = sanitized_title.split("_")
        truncated_title = ""
        for word in words:
            candidate = f"feature/{task_code}__{truncated_title}_{word}".strip("_")
            if len(candidate) > 80:
                break
            truncated_title = f"{truncated_title}_{word}".strip("_")
        branch_base = f"feature/{task_code}__{truncated_title}"
    return branch_base


def stash_changes():
    """Stash and apply local changes if any."""
    stash_list = run_command("git stash list")
    if stash_list:
        print("Modifications locales détectées.")
        if input("Voulez-vous stasher vos modifications actuelles ? (y/n) ").lower() == "y":
            run_command("git stash")
            print("Modifications stashées.")
            if input("Voulez-vous appliquer les modifications stashées ? (y/n) ").lower() == "y":
                run_command("git stash apply")
                print("Modifications réappliquées.")


def list_branches():
    """Liste les noms des branches distantes."""
    branches = run_command("git branch -a").split("\n")
    cleaned_branches = []
    for branch in branches:
        branch = branch.strip()
        if branch.startswith("remotes/origin/"):
            cleaned_branches.append(branch.replace("remotes/origin/", "")) 
    return cleaned_branches


def select_branch():
    """Display branch options and let the user select one."""
    branches = list_branches()
    print("\n--- Sélectionnez une branche de base ---")
    for i, branch in enumerate(branches, start=1):
        print(f"{i}. {branch}")
    while True:
        try:
            choice = int(input("Entrez le numéro de la branche : "))
            if 1 <= choice <= len(branches):
                return branches[choice - 1]
            else:
                print("Choix invalide. Veuillez entrer un numéro valide.")
        except ValueError:
            print("Entrée invalide. Veuillez entrer un numéro.")


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
    transition_mapping = {
        "en cours": "2",  # Exemple d'ID de transition
        "en revue": "3",  # Exemple d'ID de transition
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
        print(f"Erreur lors de la transition de la tâche Jira {task_number} : {response.status_code} {response.text}")


def get_valid_task_number(config):
    """Prompt the user for a valid Jira task number."""
    while True:
        task_number = input("Entrez le numéro de la tâche Jira : ").strip()
        task_data = jira_task_exists(config, task_number)
        if task_data:
            return task_number, task_data["fields"]["summary"]


def start_new_task(config):
    """Handle starting a new task."""
    task_number, title = get_valid_task_number(config)
    branch_name = generate_branch_name(task_number, title)
    print(f"Nom de branche proposé : {branch_name}")
    branch_name = input(f"Entrez un nom de branche ou appuyez sur Entrée pour utiliser '{branch_name}' : ").strip() or branch_name

    print("\nSélectionnez la branche de base pour la nouvelle branche.")
    base_branch = select_branch()

    stash_changes()

    run_command(f"git checkout {base_branch}")
    run_command(f"git pull origin {base_branch}")
    run_command(f"git checkout -b {branch_name}")
    jira_transition(config, task_number, "en cours")
    print(f"Branche {branch_name} créée à partir de {base_branch} et la tâche Jira est maintenant en cours.")


def fix_development(config):
    """Handle fixing a development."""
    task_number, title = get_valid_task_number(config)
    branch_name = generate_branch_name(task_number, title)
    print(f"Nom de branche proposé pour le fix : {branch_name}")
    branch_name = input(f"Entrez un nom de branche ou appuyez sur Entrée pour utiliser '{branch_name}' : ").strip() or branch_name

    print("\nVérification de l'existence de la branche 'develop'...")
    if "develop" not in list_branches():
        print("La branche 'develop' n'existe pas dans ce dépôt. Impossible de continuer.")
        return

    stash_changes()

    run_command("git checkout develop")
    run_command(f"git checkout -b {branch_name}")
    jira_transition(config, task_number, "en cours")
    print(f"Branche {branch_name} créée à partir de develop et la tâche Jira est maintenant en cours.")


def end_development(config):
    """Handle ending the development of a task."""
    task_number, _ = get_valid_task_number(config)
    commit_message = input("Entrez le message du commit : ").strip()

    run_command("git add .")
    run_command(f"git commit -m \"{commit_message}\"")
    jira_transition(config, task_number, "en revue")
    print(f"Modifications commitées avec le message : {commit_message}. La tâche Jira est maintenant en revue.")


def main():
    config = load_config()
    if not config:
        print("Impossible de charger la configuration. Vérifiez 'config.json'.")
        return

    while True:
        print("\n--- Gestion des Tâches Jira ---")
        print("1. Nouvelle tâche")
        print("2. Fin de développement")
        print("3. Fix d'un développement")
        print("4. Quitter")
        choice = input("Choisissez une option : ").strip()

        if choice == "1":
            start_new_task(config)
        elif choice == "2":
            end_development(config)
        elif choice == "3":
            fix_development(config)
        elif choice == "4":
            print("Au revoir !")
            break
        else:
            print("Choix invalide. Veuillez réessayer.")


if __name__ == "__main__":
    main()