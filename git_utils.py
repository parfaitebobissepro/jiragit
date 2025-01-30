import subprocess
from string_utils import remove_accents # Import from string_utils

def run_command(command):
    """Run a shell command and return its output."""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution de la commande : {command}\n{e.stderr}")
        return None

def generate_branch_name(task_code, title):
    """Generate a branch name based on the task code and title."""
    sanitized_title = remove_accents("_".join(title.lower().split()))
    branch_base = f"feature/{task_code}_{sanitized_title}"

    # Truncate title if branch name exceeds 80 characters
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

def list_remote_branches():
    """List remote branch names."""
    branches = run_command("git branch -a").split("\n")
    cleaned_branches = []
    for branch in branches:
        branch = branch.strip()
        if branch.startswith("remotes/origin/"):
            cleaned_branches.append(branch.replace("remotes/origin/", ""))
    return cleaned_branches

def select_branch():
    """Display branch options and let the user select one."""
    branches = list_remote_branches()
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