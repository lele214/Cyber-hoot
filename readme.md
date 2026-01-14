
## Cyber-hoot

Notre plateforme Cyber-hoot (pour “cyber” et “kahoot”) propose des quiz sur le thème de la Cybersécurité. Aujourd’hui, à l’ère d’un monde hyper-connecté, le nombre de cyberattaques n’a jamais été aussi important : il est prévu jusqu’à une cyberattaque toutes les 2 secondes d’ici 2031. Et l’un des facteurs de réussite de ces attaques est toujours relatif à une chose : le facteur humain. En effet, ce sont les erreurs que nous faisons tous les jours qui nous rendent le plus vulnérable. Et la raison est essentiellement à cause d’un manque d’information ou de formation. Notre plateforme va proposer divers quiz de culture générale relatifs aux différentes attaques existantes, essentiellement pour sensibiliser sur les risques liés à la cybersécurité. 



## Installation

### Première installation

```bash
# Cloner le repository
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
