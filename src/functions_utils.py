from .utils import *
from .global_const import TaskStatus, WorkflowTransition,REMOTE_REPO_NAME
from src.utils.ansi import get_colored_text, BRIGHT_CYAN


#TODO: Exporter toutes commandes git dans git_utils.py
def handle_task_creation():
    """Handle the creation of a new task or fix."""
    task_number, title, type_task = get_task_infos()

    if not task_number :
        return

    branch_name = generate_branch_name(task_number, title, type=type_task)
    print(f"Nom de branche proposé : {get_colored_text(branch_name,BRIGHT_CYAN)}")
    branch_name = input(f"Entrez un nom de branche ou appuyez sur Entrée pour utiliser '{branch_name}' : ").strip() or branch_name

    if type_task == "Bug":
        base_branch = "develop"
        print(f"\nBranche de base par défaut pour un fix : {base_branch}")
    else:
        print("\nSélectionnez la branche de base pour la nouvelle branche.")
        base_branch = select_branch()

    is_changes_saved = stash_changes()

    if run_command(f"git checkout {base_branch}") != None:
        print(f"Changement de branche vers {base_branch}.")
        if run_command(f"git pull {REMOTE_REPO_NAME} {base_branch}") != None:
            print(f"Pull effectué depuis la branche {base_branch}.")
            if run_command(f"git checkout -b {branch_name}") != None:
                print(f"Branche {branch_name} créée à partir de {base_branch}")
                if not jira_task_is_in_status(task_number, TaskStatus.IN_PROGRESS.value):
                    jira_transition(task_number, WorkflowTransition.IN_PROGRESS)
                if is_changes_saved:
                    apply_stashed_changes()

#TODO : Refractorer cette fonction et mettre les tests
def commit_and_push_changes(task_number, commit_message, jira_task_status_enum, jira_workflow_transition_enum, create_pr=False):
    """Handle committing and pushing changes, and updating Jira status."""
    final_commit_message = f"feat:{task_number} - {commit_message}"
    print(f"Le message qui sera commiter est le suivant: \n \n \t {final_commit_message}")

    staged_files_selected = select_files_for_commit()

    """Vérifie s'il existe des fichiers dans la zone de staging à commiter."""
    staged_files = run_command("git diff --cached --name-only")

    """Si des fichiers sont déjà stage, et n'ont pas été sélectionnés, on les affiche comme déjà en staging et prevenir qu'ils seront commités."""
    print(f"staged_files:{staged_files}")
    if staged_files and staged_files.strip():
        staged_files = staged_files.split("\n")

        """Fichiers présents dans staged_files mais pas dans staged_files_selected."""
        if staged_files_selected:
            staged_files = [file for file in staged_files if file not in staged_files_selected]

        if staged_files and staged_files != []:
            print("Fichiers déjà en staging :")
            print("\n".join(staged_files))
            if input("Voulez-vous continuer avec ces fichiers déjà en staging ? (y/n) ").lower() != "y":
                return

        if run_command(f"git commit -m \"{final_commit_message}\"") != None:
            print(f"Modifications commitées avec le message : {commit_message}.")
            
            branch_name = run_command("git rev-parse --abbrev-ref HEAD").strip()
            if run_command(f"git push -u {REMOTE_REPO_NAME} {branch_name}") != None:
                if not jira_task_is_in_status(task_number, jira_task_status_enum.value):
                    jira_transition(task_number, jira_workflow_transition_enum)

                mr_url = None
                
                if create_pr:
                    mr_url = create_merge_request(branch_name, f"Merge branch {branch_name} into develop")
                jira_add_comment(task_number, commit_message, mr_url)
    else:
        print("Aucun fichier à commiter. Opération annulée.")
        return