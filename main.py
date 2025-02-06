from src import *

def main():
    if not GLOBAL_JSON_CONFIG:
        print("Impossible de charger la configuration. Vérifiez 'config.json'.")
        return

    options = {
        "1": ("Nouveau développement", start_new_task),
        "2": ("Continuer le développement", continue_development),
        "3": ("Fin de développement", end_development),
        "4": ("Quitter", lambda bye: print("Au revoir !"))
    }

    while True:
        print("\n--- Gestion des Tâches Jira ---")
        for key, (description, _) in options.items():
            print(f"{key}. {description}")
        choice = input("Choisissez une option : ").strip()

        if choice in options:
            if choice == "4":
                options[choice][1](bye=True)
                break
            else:
                options[choice][1]()
        else:
            print("Choix invalide. Veuillez réessayer.")

if __name__ == "__main__":
    main()