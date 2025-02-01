from jira_utils import jira_task_exists, jira_transition, get_valid_task_number, load_config, jira_add_comment, jira_task_is_in_status
from git_utils import run_command, generate_branch_name, stash_changes, list_remote_branches, select_branch, getCurrentTaskNumber, select_files_for_commit
from gitlab_utils import create_merge_request


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
    if not jira_task_is_in_status(config, task_number, "en cours"):
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
    task_number = getCurrentTaskNumber()
    print(f"Le code de la tâche actuelle est le suivant {task_number}")
    commit_message = input("Entrez le message du commit : ").strip()
    final_commit_message = f"feat:{task_number} - {commit_message}"

    print(f"Le message qui sera commiter est le suivant: \n \n \t {final_commit_message}")

    """If no files are modified, return."""
    if not select_files_for_commit():
        return

    run_command(f"git commit -m \"{final_commit_message}\"")
    """Transition the Jira task to 'en revue' if not already.""" 
    jira_transition(config, task_number, "en revue")
    jira_add_comment(config, task_number, commit_message)
    print(f"Modifications commitées avec le message : {commit_message}. La tâche Jira est maintenant en revue.")

    """Get current branch name and push changes."""
    branch_name = run_command("git rev-parse --abbrev-ref HEAD").strip()

    """TODO: Implement choice between gitlab and github."""
    """Ask if want to create a pull request on Gitlab."""
    if input("Voulez-vous créer une pull request ? (y/n) ").lower() == "y":
        run_command(f"git push -u origin {branch_name}")
        create_merge_request(config, branch_name, "Merge branch "+ branch_name + " into develop")
    else:
        run_command(f"git push -u origin {branch_name}")

def continue_development(config):
    """Handle continuing the development of a task."""
    task_number = getCurrentTaskNumber()
    print(f"Le code de la tâche actuelle est le suivant {task_number}")
    commit_message = input("Entrez le message du commit : ").strip()
    final_commit_message = f"feat:{task_number} - {commit_message}"

    print(f"Le message qui sera commiter est le suivant: \n \n \t {final_commit_message}")

    """If no files are modified, return."""
    if not select_files_for_commit():
        return

    run_command(f"git commit -m \"{final_commit_message}\"")
    """Transition the Jira task to 'en cours' if not already."""
    if not jira_task_is_in_status(config, task_number, "en cours"):
        jira_transition(config, task_number, "en cours")
    jira_add_comment(config, task_number, commit_message)
    print(f"Modifications commitées avec le message : {commit_message}. La tâche Jira est maintenant en cours.")

    """Get current branch name and push changes."""
    branch_name = run_command("git rev-parse --abbrev-ref HEAD").strip()
    run_command(f"git push -u origin {branch_name}")

def main():
    config = load_config()
    if not config:
        print("Impossible de charger la configuration. Vérifiez 'config.json'.")
        return

    while True:
        print("\n--- Gestion des Tâches Jira ---")
        print("1. Nouvelle tâche")
        print("2. Continuer le développement")
        print("3. Fin de développement")
        print("4. Fix d'un développement")
        print("5. Quitter")
        choice = input("Choisissez une option : ").strip()

        if choice == "1":
            start_new_task(config)
        elif choice == "2":
            continue_development(config)
        elif choice == "3":
            end_development(config)
        elif choice == "4":
            fix_development(config)
        elif choice == "5":
            print("Au revoir !")
            break
        else:
            print("Choix invalide. Veuillez réessayer.")


if __name__ == "__main__":
    main()