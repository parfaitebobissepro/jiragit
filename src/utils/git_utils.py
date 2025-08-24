import re
from .string_utils import remove_accents
from .run_command import run_command
from src.global_const import GLOBAL_JSON_CONFIG, REMOTE_REPO_NAME

def generate_branch_name(task_code, title, type):
    """Mapping between Jira task types and branch prefixes."""
    """TODO: Prendre en compte les hotfixes"""
    type_mapping = GLOBAL_JSON_CONFIG["jira"]["task_type_mapping"]

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
    """Stash local changes if any."""
    stash_list = run_command("git status --short").split("\n")

    """Print the list of modified files."""
    print("\n--- Fichiers modifiés ---")
    for file in stash_list:
        print(file)

    if stash_list and stash_list[0]:
        if input("\nModifications locales détectées. Voulez-vous stasher vos modifications actuelles ? (y/n) ").lower() == "y":
            run_command("git stash")
            print("Modifications stashées.")
            return True
    return False

def apply_stashed_changes():
    """Apply stashed changes if user confirms."""
    if input("Voulez-vous appliquer les modifications stashées ? (y/n) ").lower() == "y":
        run_command("git stash apply")
        print("Modifications réappliquées.")

def list_remote_branches():
    """List remote branch names."""
    branches = run_command("git branch -a").split("\n")
    cleaned_branches = []
    for branch in branches:
        branch = branch.strip()
        if branch.startswith(f"remotes/{REMOTE_REPO_NAME}/"):
            cleaned_branches.append(branch.replace(f"remotes/{REMOTE_REPO_NAME}/", ""))
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
    try:
        base_name_branch = branch_name.split("_")[0]
        task_number = base_name_branch.split("/")[1]
        return task_number
    except IndexError:
        print("Erreur: Vous n'êtes pas sur une branche nommée selon les conventions (par exemple, develop).")
        raise SystemExit("Veuillez régler le problème puis relancer la commande.")

def select_files_for_commit():
    """Allow user to select files to commit, handling renamed files and their new locations.
    Only propose files not already staged.
    """
    while True:
        # Get unstaged files
        files_raw = run_command("git status --short").split("\n")
        # Get staged files
        staged_raw = run_command("git diff --cached --name-only").split("\n")
        staged_files = set(f.strip().replace('"', '') for f in staged_raw if f.strip())

        files = []
        file_map = {}  # Map displayed name to actual file path

        for file_line in files_raw:
            file_line = file_line.strip()
            if not file_line:
                continue
            # Handle renamed files (e.g., "R  oldname -> newname")
            if "->" in file_line:
                parts = file_line.split("->")
                old_path = parts[0].strip()[2:].strip()
                new_path = parts[1].strip()
                display_name = f"{old_path} -> {new_path}"
                # Only propose if new_path is not staged
                if new_path not in staged_files:
                    files.append(display_name)
                    file_map[display_name] = new_path
            else:
                file_path = file_line[2:].strip().replace('"', '')
                # Only propose if file_path is not staged
                if file_path and file_path not in staged_files:
                    files.append(file_path)
                    file_map[file_path] = file_path

        if not files:
            print("Aucun fichier modifié non ajouté trouvé.")
            return

        selected_files = []

        print("\n--- Fichiers/Dossiers modifiés (non ajoutés) ---")
        print("0. Revenir en arrière")
        for i, file in enumerate(files, start=1):
            print(f"{i}. {file}")
        print(". Ajouter tous les fichiers/dossiers")
        print("f. Terminer la sélection et continuer")

        while True:
            choice = input("Entrez le numéro du fichier à ajouter ('.' pour tous, 'f' pour finir) : ").strip()

            if choice == "0":
                print("Opération annulée, retour au menu principal.")
                return

            if choice == ".":
                selected_files = files[:]  # Ajouter tous les fichiers proposés
                break

            if choice == "f":
                break

            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(files):
                    file = files[choice_num - 1]
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

        if not selected_files:
            print("Aucun fichier sélectionné")
            return

        confirm = input("Confirmez-vous l'ajout de ces fichiers au commit ? (y/n) : ").strip().lower()
        if confirm == "y":
            # Ajout de chaque fichier individuellement, pour les renommés on prend le nouveau chemin
            for file in selected_files:
                run_command(f'git add "{file_map[file]}"')
            print("✅ Fichiers ajoutés avec succès.")
            return [file_map[file] for file in selected_files]
        else:
            print("Sélection annulée, veuillez recommencer.")
