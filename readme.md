## Installation

### Première installation

```bash
git clone https://github.com/lele214/Cyber-hoot
cd Cyber-hoot
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

L'application sera accessible sur http://localhost:5000

### Après chaque git pull

```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Commandes disponibles

```bash
docker compose up -d              # Démarre l'application
docker compose down               # Arrête l'application
docker compose restart            # Redémarre l'application
docker compose logs -f app        # Affiche les logs de l'application
docker compose logs -f db         # Affiche les logs de la base de données
docker compose exec app sh        # Ouvre un shell dans le conteneur app
docker compose exec db mysql -uroot -prootpassword cyberhoot  # Shell MySQL
docker compose ps                 # Affiche l'état des conteneurs
```

### Réinitialiser la base de données

```bash
docker compose down
docker volume rm cyber-hoot_db_data
docker compose up -d
```

## Structure du projet

```
Cyber-hoot/
├── app/                   # Code de l'application Flask
│   ├── __init__.py        # Factory pattern Flask
│   ├── main.py            # Point d'entrée
│   ├── config.py          # Configuration (dev/prod)
│   ├── database.py        # Configuration SQLAlchemy
│   ├── routes/            # Routes Flask
│   ├── templates/         # Templates Jinja2
│   └── static/            # Fichiers statiques (CSS, JS)
├── docker/                # Configuration Docker
│   ├── Dockerfile
│   └── wait-for-it.sh     # Script d'attente de la DB
├── data/init/             # Scripts SQL d'initialisation
└── docker-compose.yml     # Configuration des services
```

## Base de données

La base de données MySQL est automatiquement créée avec :
- `data/init/01-schema.sql` - Schéma de la base de données
- `data/init/02-seed-data.sql` - Données de test
