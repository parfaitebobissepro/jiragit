from .utils import load_config
from enum import Enum
from src.utils.ansi import *

GLOBAL_JSON_CONFIG = load_config()

REMOTE_REPO_NAME = GLOBAL_JSON_CONFIG["git"]["remote_repository_name"]

class WorkflowTransition(Enum):
    IN_PROGRESS = GLOBAL_JSON_CONFIG["jira"]["transitions"]["IN_PROGRESS"]
    IN_REVIEW = GLOBAL_JSON_CONFIG["jira"]["transitions"]["IN_REVIEW"]

class TaskStatus(Enum):
    IN_PROGRESS = GLOBAL_JSON_CONFIG["jira"]["task_status"]["IN_PROGRESS"]
    IN_REVIEW = GLOBAL_JSON_CONFIG["jira"]["task_status"]["IN_REVIEW"]

class TaskStatus(Enum):
    IN_PROGRESS = GLOBAL_JSON_CONFIG["jira"]["task_status"]["IN_PROGRESS"]
    IN_REVIEW = GLOBAL_JSON_CONFIG["jira"]["task_status"]["IN_REVIEW"]

JIRA_STATUS_CATEGORY_COLOR = {
    "A faire" : CYAN,
    "En cours" : YELLOW,
    "Terminé" : GREEN,
}

JIRA_TYPE_ISSUE_COLOR = {
    "Tâche" : BLUE,
    "Bug" : RED
}
    