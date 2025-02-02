import subprocess
import re
from string_utils import remove_accents # Import from string_utils

def run_command(command):
    """Run a shell command and return its output."""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'exécution de la commande : {command}\n{e.stderr}")
        return None

def generate_branch_name(task_code, title, type):
    """Mapping between Jira task types and branch prefixes."""
    """TODO: Prendre en compte les hotfixes"""
    type_mapping = {
        "Story": "story",
        "Bug": "fix",
        "Tâche": "feature",
        "Epic": "epic"
    }

    type = type_mapping.get(type, "feature")

    """Generate a branch name based on the task code and title."""
    sanitized_title = remove_accents("_".join(title.lower().split()))
    sanitized_title = re.sub(r'[^a-z0-9_]+', '_', sanitized_title)  # Replace special characters with '_'
    sanitized_title = re.sub(r'_+', '_', sanitized_title)  # Replace consecutive '_' with a single '_'
    branch_base = f"{type}/{task_code}_{sanitized_title}"

    # Truncate title if branch name exceeds 80 characters
    if len(branch_base) > 80:
        words = sanitized_title.split("_")
        truncated_title = ""
        for word in words:
            candidate = f"{type}/{task_code}__{truncated_title}_{word}".strip("_")
            if len(candidate) > 80:
                break
            truncated_title = f"{truncated_title}_{word}".strip("_")
        branch_base = f"{type}/{task_code}__{truncated_title}"
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

def getCurrentTaskNumber():
    """Get the current Jira task number from the branch name."""
    branch_name = run_command("git rev-parse --abbrev-ref HEAD")
    base_name_branch = branch_name.split("_")[0]
    task_number = base_name_branch.split("/")[1]
    return task_number

def select_files_for_commit():
    """Allow user to select files to commit, excluding deleted files, with options to add all files, finish selection, or go back."""
    while True:
        files_raw = run_command("git status --short").split("\n")
        
        # Exclure les fichiers supprimés (ceux qui commencent par "D")
        files = [file.strip().split()[-1] for file in files_raw if file.strip() and not file.strip().startswith("D")]

        if not files:
            print("Aucun fichier modifié trouvé.")
            return

        selected_files = []

        print("\n--- Fichiers modifiés (hors fichiers supprimés) ---")
        print("0. Revenir en arrière")
        for i, file in enumerate(files, start=1):
            print(f"{i}. {file}")
        print(". Ajouter tous les fichiers")
        print("f. Terminer la sélection et continuer")

        while True:
            choice = input("Entrez le numéro du fichier à ajouter ('.' pour tous, 'f' pour finir) : ").strip()

            if choice == "0":
                print("Opération annulée, retour au menu principal.")
                return

            if choice == ".":
                selected_files = files[:]  # Ajouter tous les fichiers sauf supprimés
                break

            if choice == "f":
                if not selected_files:
                    print("Vous devez sélectionner au moins un fichier avant de terminer.")
                    continue
                break

            try:
                choice = int(choice)
                if 1 <= choice <= len(files):
                    file = files[choice - 1]
                    if file not in selected_files:
                        selected_files.append(file)
                        print(f"Le fichier {file} a été ajouté à la sélection.")
                    else:
                        print(f"Le fichier {file} est déjà sélectionné.")
                else:
                    print("Choix invalide. Veuillez entrer un numéro valide.")
            except ValueError:
                print("Entrée invalide. Veuillez entrer un numéro.")

        # Affichage des fichiers sélectionnés
        print("\n--- Fichiers sélectionnés ---")
        for file in selected_files:
            print(f"- {file}")

        confirm = input("Confirmez-vous l'ajout de ces fichiers au commit ? (y/n) : ").strip().lower()
        if confirm == "y":
            # Correction ici : Ajout de chaque fichier individuellement
            for file in selected_files:
                run_command(f"git add {file}")
            print("✅ Fichiers ajoutés avec succès.")
            return selected_files
        else:
            print("Sélection annulée, veuillez recommencer.")