import subprocess

def run_command(command):
    """Exécute une commande shell et retourne sa sortie."""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'exécution de la commande : {command}\n{e.stderr}")
        return None