from jira_utils import jira_task_exists, jira_transition, get_valid_task_number, load_config
from git_utils import run_command, generate_branch_name, stash_changes, list_remote_branches, select_branch


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
    if "develop" not in list_remote_branches(): # Use the new function
        print("La branche 'develop' n'existe pas dans ce dépôt. Impossible de continuer.")

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