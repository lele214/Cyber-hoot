# Cyber-hoot

Plateforme de quiz sur la cybersécurité, inspirée de Kahoot. L'objectif est de sensibiliser aux risques cyber à travers des quiz interactifs de culture générale sur les différentes cyberattaques existantes.

## Tech Stack

- **Backend** : Flask, SQLAlchemy, PyMySQL
- **Frontend** : Jinja2, Tailwind CSS
- **Base de données** : MySQL 8.0
- **Infrastructure** : Docker Compose
- **Admin DB** : Adminer
- **Migrations** : Alembic
- **Analyse de fichiers** : VirusTotal API v3
- **Tests** : pytest (SQLite en mémoire)

## Prérequis

- [Docker](https://www.docker.com/) et Docker Compose
- [just](https://github.com/casey/just) — command runner (voir `docs/justfile.md`)
- Python 3.11+ (pour les tests unitaires uniquement, hors Docker)

## Installation

### 1. Cloner le projet

```bash
git clone https://github.com/lele214/Cyber-hoot
cd Cyber-hoot
```

### 2. Configurer l'environnement

Copier le fichier d'exemple et adapter les valeurs :

```bash
cp .env.example .env
```

Créer le dossier `secrets/` avec les fichiers de mots de passe :

```bash
mkdir secrets
echo "votre_mot_de_passe" > secrets/db_password.txt
echo "votre_mot_de_passe_root" > secrets/db_root_password.txt
```

> Pour activer le scan VirusTotal, ajouter également :
> ```bash
> echo "votre_cle_api" > secrets/api_key
> ```
> Sans ce fichier, le scan est simplement ignoré.

### 3. Lancer l'application

```bash
just build      # build + démarrage
# ou
just dev        # démarrage avec logs visibles
```

L'application est accessible sur :
- **App** : http://localhost:5000
- **Adminer** : http://localhost:8181

### Après un git pull

```bash
just build
```

### Réinitialiser la base de données

```bash
just db-reset   # ⚠️ supprime toutes les données
```

## Commandes (just)

Toutes les commandes du projet passent par `just`. Voir `docs/justfile.md` pour le détail.

```bash
just --list     # affiche toutes les commandes disponibles
```

### Application

| Commande | Description |
|---|---|
| `just dev` | Démarre avec logs visibles |
| `just start` | Démarre en arrière-plan |
| `just stop` | Arrête les conteneurs |
| `just build` | Rebuild et redémarre |
| `just logs` | Logs de l'app en temps réel |
| `just shell` | Shell dans le conteneur app |
| `just status` | État des conteneurs |

### Base de données

| Commande | Description |
|---|---|
| `just db-shell` | Shell MySQL |
| `just db-reset` | ⚠️ Remet la DB à zéro |

### Migrations Alembic

| Commande | Description |
|---|---|
| `just migrate` | Applique les migrations en attente |
| `just migrate-new "description"` | Crée une migration depuis les modèles |
| `just migrate-status` | Historique et version actuelle |
| `just migrate-down` | Annule la dernière migration |

### Tests unitaires

| Commande | Description |
|---|---|
| `just test` | Tous les tests (verbeux) |
| `just test-short` | Résumé rapide |
| `just test-fail-fast` | S'arrête au premier échec |
| `just test-debug` | Affiche les `print()` |
| `just test-run <cible>` | Un fichier ou un test précis |

```bash
# Exemples
just test-run test/test_quiz.py
just test-run test/test_quiz.py::test_quiz_creation_model
```

## Structure du projet

```
Cyber-hoot/
├── app/
│   ├── __init__.py              # Factory Flask (create_app)
│   ├── config.py                # Configurations (dev / prod / testing)
│   ├── decorators.py            # @login_required, @role_required
│   ├── extensions.py            # SQLAlchemy + db_transaction()
│   ├── models/
│   │   └── models.py            # Tous les modèles SQLAlchemy
│   ├── routes/
│   │   ├── auth.py              # Authentification (login, register, reset)
│   │   ├── main_routes.py       # Quiz publics + soumission des résultats
│   │   └── profile.py           # Dashboards admin / creator / player
│   ├── services/
│   │   └── virustotal.py        # Scan de fichiers via VirusTotal API v3
│   ├── static/
│   │   ├── js/                  # Scripts quiz (front)
│   │   └── src/input.css        # Tailwind source
│   ├── templates/
│   │   ├── auth/                # Login, register, reset password
│   │   ├── profile/             # Dashboards (admin, creator, player)
│   │   └── quiz/                # Pages quiz
│   └── uploads/                 # Fichiers media uploadés (images quiz)
├── alembic/                     # Migrations de base de données
│   └── versions/                # Fichiers de migration générés
├── database/
│   └── db_schemaV3-3.sql        # Schéma SQL initial
├── docs/
│   ├── alembic.md               # Guide migrations Alembic
│   └── justfile.md              # Guide commandes just
├── secrets/                     # Mots de passe Docker secrets (non versionné)
├── test/
│   ├── conftest.py              # Fixtures pytest partagées
│   ├── test_hash.py             # Tests hachage de mots de passe
│   ├── test_login.py            # Tests authentification
│   ├── test_registration.py     # Tests inscription
│   ├── test_quiz.py             # Tests création et modification de quiz
│   ├── test_badges.py           # Tests badges
│   ├── test_virustotal.py       # Tests service VirusTotal (API mockée)
│   ├── test_scores.py           # Tests scores et résultats
│   └── seed_data.sql            # Données de référence pour le dev
├── alembic.ini                  # Configuration Alembic
├── docker-compose.yml
├── Dockerfile
├── justfile                     # Commandes du projet
├── pytest.ini                   # Configuration pytest
├── requirements.txt
├── run.py                       # Point d'entrée Flask
└── .env                         # Variables d'environnement (non versionné)
```

## Architecture — Modèles de données

```
User ──────┬── (many-to-many) ── Role
           ├── Quiz (créateur)
           ├── Result
           ├── UserBadge
           ├── Notification
           └── ConnectionLog

Quiz ──────┬── Question ── Response ── Media
           ├── Badge ── UserBadge
           └── Result
```

| Modèle | Table | Description |
|---|---|---|
| `User` | `USER` | Utilisateurs de la plateforme |
| `Role` | `ROLES` | Rôles : `admin`, `creator`, `player` |
| `Quiz` | `QUIZ` | Quiz avec titre, difficulté, statut, catégorie |
| `Question` | `QUESTION` | Questions d'un quiz |
| `Response` | `RESPONSE` | Réponses d'une question |
| `Media` | `MEDIA` | Images ou liens attachés aux questions/réponses |
| `Badge` | `BADGES` | Badges liés à un quiz |
| `UserBadge` | `user_badges` | Badges obtenus par un utilisateur |
| `Result` | `RESULT` | Résultats de quiz (score, date, réponses) |
| `Notification` | `NOTIFICATIONS` | Notifications utilisateur |
| `ConnectionLog` | `CONNECTION_LOG` | Historique de connexions |

## Rôles utilisateurs

| Rôle | Permissions |
|---|---|
| **Player** | Répondre aux quiz publiés, consulter ses scores et badges |
| **Creator** | Créer, modifier et soumettre des quiz pour validation |
| **Admin** | Valider/rejeter les quiz, gérer les utilisateurs et badges |

## Statuts d'un quiz

```
DRAFT → PENDING → PUBLISHED
                ↘ DRAFT (rejet)
PUBLISHED → MODIFIED (après édition)
```

## Tests unitaires

Les tests s'exécutent entièrement **hors Docker**, avec une base SQLite en mémoire. Aucune dépendance à MySQL ou à une clé VirusTotal n'est requise.

```bash
pip install pytest
just test
```

61 tests couvrant : hachage des mots de passe, authentification, inscription, création/modification de quiz, badges, scores, service VirusTotal (API mockée).
