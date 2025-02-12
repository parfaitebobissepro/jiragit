from .utils import *
from .global_const import TaskStatus, WorkflowTransition,REMOTE_REPO_NAME

def handle_task_creation():
    """Handle the creation of a new task or fix."""
    task_number, title, type_task = get_task_infos()
    branch_name = generate_branch_name(task_number, title, type=type_task)
    print(f"Nom de branche proposé : {branch_name}")
    branch_name = input(f"Entrez un nom de branche ou appuyez sur Entrée pour utiliser '{branch_name}' : ").strip() or branch_name

    if type_task == "Bug":
        base_branch = "develop"
        print(f"\nBranche de base par défaut pour un fix : {base_branch}")
    else:
        print("\nSélectionnez la branche de base pour la nouvelle branche.")
        base_branch = select_branch()

    stash_changes()

    if run_command(f"git checkout {base_branch}") != None:
        print(f"Changement de branche vers {base_branch}.")
        if run_command(f"git pull {REMOTE_REPO_NAME} {base_branch}") != None:
            print(f"Pull effectué depuis la branche {base_branch}.")
            if run_command(f"git checkout -b {branch_name}") != None:
                print(f"Branche {branch_name} créée à partir de {base_branch}")
                if not jira_task_is_in_status(task_number, TaskStatus.IN_PROGRESS.value):
                    jira_transition(task_number, WorkflowTransition.IN_PROGRESS)

def commit_and_push_changes(task_number, commit_message, jira_task_status_enum, jira_workflow_transition_enum, create_pr=False):
    """Handle committing and pushing changes, and updating Jira status."""
    final_commit_message = f"feat:{task_number} - {commit_message}"
    print(f"Le message qui sera commiter est le suivant: \n \n \t {final_commit_message}")

    if not select_files_for_commit():
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
