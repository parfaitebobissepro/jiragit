from git_utils import getCurrentTaskNumber
from functions_utils import handle_task_creation, commit_and_push_changes


def start_new_task(config):
    """Handle starting a new task."""
    handle_task_creation(config)

def end_development(config):
    """Handle ending the development of a task."""
    task_number = getCurrentTaskNumber()
    print(f"Le code de la tâche actuelle est le suivant {task_number}")
    commit_message = input("Entrez le message du commit : ").strip()
    commit_and_push_changes(config, task_number, commit_message, "en revue", create_pr=True)

def continue_development(config):
    """Handle continuing the development of a task."""
    task_number = getCurrentTaskNumber()
    print(f"Le code de la tâche actuelle est le suivant {task_number}")
    commit_message = input("Entrez le message du commit : ").strip()
    commit_and_push_changes(config, task_number, commit_message, "en cours")