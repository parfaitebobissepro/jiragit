from jira_utils import get_task_infos, jira_transition, jira_add_comment, jira_task_is_in_status
from git_utils import run_command, generate_branch_name, stash_changes, select_files_for_commit, select_branch
from gitlab_utils import create_merge_request

def handle_task_creation(config):
    """Handle the creation of a new task or fix."""
    task_number, title, type_task = get_task_infos(config)
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

    run_command(f"git checkout {base_branch}")
    run_command(f"git pull origin {base_branch}")
    run_command(f"git checkout -b {branch_name}")
    if not jira_task_is_in_status(config, task_number, "en cours"):
        jira_transition(config, task_number, "en cours")
    print(f"Branche {branch_name} créée à partir de {base_branch} et la tâche Jira est maintenant en cours.")

def commit_and_push_changes(config, task_number, commit_message, jira_status, create_pr=False):
    """Handle committing and pushing changes, and updating Jira status."""
    final_commit_message = f"feat:{task_number} - {commit_message}"
    print(f"Le message qui sera commiter est le suivant: \n \n \t {final_commit_message}")

    if not select_files_for_commit():
        return

    run_command(f"git commit -m \"{final_commit_message}\"")
    if not jira_task_is_in_status(config, task_number, jira_status):
        jira_transition(config, task_number, jira_status)
    jira_add_comment(config, task_number, commit_message)
    print(f"Modifications commitées avec le message : {commit_message}. La tâche Jira est maintenant {jira_status}.")

    branch_name = run_command("git rev-parse --abbrev-ref HEAD").strip()
    run_command(f"git push -u origin {branch_name}")

    if create_pr:
        create_merge_request(config, branch_name, f"Merge branch {branch_name} into develop")