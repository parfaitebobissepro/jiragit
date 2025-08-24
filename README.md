# Jiragit 🛠️🚀

Jiragit est un outil CLI permettant de faciliter l'intégration entre **Jira** et **GitLab**.
Il propose une automatisation du workflow **Jira** et des interactions avec **GitLab**, afin de fluidifier le développement des fonctionnalités et corrections de bugs.
## 💻 Prérequis

Avant de commencer, assurez-vous d'avoir **Python** installé sur votre ordinateur :
- Python 3.6 ou supérieur
- Accès aux commandes Python via le terminal (`python` ou `py`)

## 📌 Installation & Lancement

### 1️⃣ Installer les dépendances 📦
```sh
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
```

### 2️⃣ Configuration 🛠️
Renommer `config-example.json` en `config.json` et y renseigner vos paramètres.

### 3️⃣ Lancer l'application 🚀
```sh
python main.py
```

## 🔧 Génération d'un exécutable

Utiliser **PyInstaller** pour créer un exécutable standalone :
```sh
pyinstaller --onefile --clean --name=jiragit --hidden-import=src --hidden-import=utils main.py
```
Récupérer `jiragit.exe` dans le dossier `dist/`, puis :
1. Déplacer l'exécutable dans le répertoire souhaité.
2. Ajouter le chemin au `PATH` :
   ```sh
   setx PATH "%PATH%;C:\chemin\vers\jiragit"
   ```
3. Placer `config.json` dans le répertoire `%JIRAGIT_HOME%`.

Pour définir la variable d'environnement `%JIRAGIT_HOME%`, utilisez la commande suivante :
```sh
setx JIRAGIT_HOME "C:\chemin\vers\jiragit"
```

## ⚙️ Utilisation

Dans un projet **Git** initialisé, exécuter simplement la commande :
```sh
jiragit
```

Le workflow Jira supporté par défaut est le suivant :

## 🚀 Fonctionnalités

### 📌 **Démarrage d'une nouvelle tâche** (Feature & Fix)
✅ Listing des tâches du sprint en cours 📋  
✅ Proposition de nom de branche basé sur le titre Jira 🔀  
✅ Proposition de **stash** et **apply** 🛠️  
✅ Pull & checkout automatique 🔄  
✅ Déplacement automatique de la tâche Jira 📌  

### 🔄 **Évolution d'une tâche en cours**
✅ Déplacement automatique de la tâche Jira 📌  
✅ Sélection des fichiers à commit 📂  
✅ Push et ajout automatique de commentaires Jira 🚀  

### 🎯 **Fin de tâche**
✅ Déplacement automatique de la tâche Jira ✅  
✅ Sélection des fichiers à commit 📂  
✅ Création automatique d'une **Merge Request** vers GitLab 🚀  

## 🛠️ Configuration

### Exemple `config.json` 📝
```json
{
    "jira": {
        "url": "https://base.atlassian.net/",
        "username": "test@email.com",
        "api_token": "<jira_api_token>",
        "board_id": "1",
        "workflow": {
            "IN_PROGRESS": "2",
            "IN_REVIEW": "3"
        },
        "task_status": {
            "IN_PROGRESS": "En cours",
            "IN_REVIEW": "Revue en cours"
        },
        "task_type_mapping": {
            "Story": "story",
            "Bug": "fix",
            "Tâche": "feature",
            "Epic": "epic"
        }
    },
    "gitlab": {
        "url": "https://gitlab.com/",
        "token": "<gitlab_token>",
        "tokens": [
            {
                "<PROJECT_NAME>": "<project_token>"
            }
        ]
    }
}
```

### 📊 Détail des propriétés

| Clé                     | Description                                      |
|-------------------------|--------------------------------------------------|
| `jira.url`              | URL de votre instance Jira                      |
| `jira.username`         | Adresse email associée à votre compte Jira      |
| `jira.api_token`        | Token API Jira                                  |
| `jira.board_id`         | ID du tableau Jira utilisé                      |
| `jira.workflow`         | Mapping des statuts Jira pour l'automatisation  |
| `jira.task_status`      | Traduction des statuts pour affichage           |
| `jira.task_type_mapping`| Correspondance des types de tâches Jira         |
| `gitlab.url`            | URL de votre instance GitLab                    |
| `gitlab.token`          | Token global GitLab (si unique pour tous)       |
| `gitlab.tokens`         | Liste des tokens spécifiques par projet         |

ℹ️ **Remarque :** Si vous utilisez un **seul token** GitLab, placez-le dans `token`. Sinon, utilisez `tokens` pour des projets spécifiques.

## ✅ Effectuer les tests 🧪

L'exécution des tests par **module** est recommandée, car la découverte automatique dans les sous-répertoires peut poser problème.

```sh
py -m unittest discover tests/ -p "test_*.py" -b -v
py -m unittest discover tests/src -p "test_*.py" -b -v
py -m unittest discover tests/src/utils -p "test_*.py" -b -v
```

Exécuter un unique test : 

```sh
 py -m unittest tests.src.test_functions_utils.TestFunctionsUtils.test_commit_and_push_changes_user_aborts_on_staged_files
```

Taux de couverture :

- Installation du module de couverture

```sh
pip install coverage 
```

- Exécution de l'analyse de couverture par **module**

```sh
coverage run -m unittest discover tests/src/utils
```

- Génération du rapport au format html

```sh
coverage html
```

## 💡 Contribution

🚀 Ce projet, dans sa **première version**, répond à un besoin spécifique et simple. Vous pouvez **le fork** et l'utiliser comme **base** pour votre propre outil.  
📢 Je ne suis pas certain de faire évoluer activement ce projet, mais vous pouvez **proposer des améliorations** et **ouvrir des issues** sur GitHub.  
🤝 J'essaierai de résoudre les problèmes signalés et de publier des mises à jour autant que possible.

## Licence

[MIT](https://choosealicense.com/licenses/mit/)

---

🔥 **Merci d'utiliser Jiragit !** 💻🐙  
Happy coding! 🎉