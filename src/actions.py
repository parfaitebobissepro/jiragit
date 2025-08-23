from .functions_utils import handle_task_creation, commit_and_push_changes
from .utils.git_utils import getCurrentTaskNumber
from .global_const import TaskStatus, WorkflowTransition
from src.utils.ansi import get_colored_text,YELLOW


def start_new_task():
    """Handle starting a new task."""
    print("Développement d'une nouvelle tâche.")
    handle_task_creation()

def end_development():
    """Handle ending the development of a task."""
    task_number = getCurrentTaskNumber()
    print(f"Le code de la tâche actuelle est le suivant : {get_colored_text(task_number,YELLOW)}")
    commit_message = input("Entrez le message du commit : ").strip()
    commit_and_push_changes(task_number, commit_message, TaskStatus.IN_REVIEW, WorkflowTransition.IN_REVIEW,create_pr=True)

def continue_development():
    """Handle continuing the development of a task."""
    task_number = getCurrentTaskNumber()
    print(f"Le code de la tâche actuelle est le suivant : {get_colored_text(task_number,YELLOW)}")
    commit_message = input("Entrez le message du commit : ").strip()
    commit_and_push_changes(task_number, commit_message, TaskStatus.IN_PROGRESS, WorkflowTransition.IN_PROGRESS)