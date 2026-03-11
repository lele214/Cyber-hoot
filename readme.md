# Cyber-hoot

Plateforme de quiz sur la cybersecurite, inspiree de Kahoot. L'objectif est de sensibiliser aux risques cyber a travers des quiz interactifs de culture generale sur les differentes cyberattaques existantes.

## Tech Stack

- **Backend** : Flask, SQLAlchemy, PyMySQL
- **Frontend** : Jinja2, Tailwind CSS
- **Base de donnees** : MySQL 8.0
- **Infrastructure** : Docker Compose
- **Admin DB** : Adminer

## Prerequis

- [Docker](https://www.docker.com/) et Docker Compose

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

Creer le dossier `secrets/` avec les fichiers de mots de passe :

```bash
mkdir secrets
echo "votre_mot_de_passe" > secrets/db_password.txt
echo "votre_mot_de_passe_root" > secrets/db_root_password.txt
```

### 3. Lancer l'application

```bash
docker compose up -d --build
```

L'application est accessible sur :
- **App** : http://localhost:5000
- **Adminer** : http://localhost:8181

### Apres un git pull

```bash
docker compose down
docker compose up -d --build
```

### Reinitialiser la base de donnees

```bash
docker compose down -v
docker compose up -d --build
```

## Commandes utiles

| Commande | Description |
|---|---|
| `docker compose up -d` | Demarrer |
| `docker compose down` | Arreter |
| `docker compose logs -f app` | Logs de l'app |
| `docker compose logs -f db` | Logs de la DB |
| `docker compose exec app sh` | Shell dans le conteneur |
| `docker compose ps` | Etat des conteneurs |

## Structure du projet

```
Cyber-hoot/
├── app/
│   ├── __init__.py            # Factory Flask
│   ├── config.py              # Configuration
│   ├── database.py            # Setup SQLAlchemy
│   ├── decorators.py          # Decorateurs custom
│   ├── extensions.py          # Extensions Flask
│   ├── models/                # Modeles SQLAlchemy
│   ├── routes/
│   │   ├── auth.py            # Authentification
│   │   ├── main_routes.py     # Routes principales
│   │   └── profile.py         # Profils utilisateurs
│   ├── static/
│   │   ├── js/                # Scripts quiz
│   │   └── src/input.css      # Tailwind source
│   └── templates/
│       ├── auth/              # Login, register, reset password
│       ├── profile/           # Dashboards (admin, creator, player)
│       └── quiz/              # Pages quiz
├── database/
│   └── db_schemaV3-3.sql      # Schema SQL
├── secrets/                   # Mots de passe Docker secrets
├── test/
│   └── seed_data.sql          # Donnees de test
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── run.py                     # Point d'entree
└── .env                       # Variables d'environnement
```

## Roles utilisateurs

- **Player** : Repond aux quiz, consulte ses scores
- **Creator** : Cree et edite des quiz
- **Admin** : Gere la plateforme
