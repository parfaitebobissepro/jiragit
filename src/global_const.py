from utils import load_config
from enum import Enum

GLOBAL_JSON_CONFIG = load_config()

class WorkflowTransition(Enum):
    IN_PROGRESS = GLOBAL_JSON_CONFIG["jira"]["transitions"]["IN_PROGRESS"]
    IN_REVIEW = GLOBAL_JSON_CONFIG["jira"]["transitions"]["IN_REVIEW"]

class TaskStatus(Enum):
    IN_PROGRESS = GLOBAL_JSON_CONFIG["jira"]["task_status"]["IN_PROGRESS"]
    IN_REVIEW = GLOBAL_JSON_CONFIG["jira"]["task_status"]["IN_REVIEW"]