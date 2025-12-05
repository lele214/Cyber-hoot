## Installation

### Première installation

```bash
# Cloner le repository
git clone https://github.com/lele214/Cyber-hoot
cd Cyber-hoot

# Lancer l'application avec Docker
docker compose up --build
```

La base de données sera automatiquement créée avec le schéma et les données de test lors du premier démarrage.

### Réinitialiser la base de données

Si vous souhaitez réinitialiser complètement la base de données avec les données de test :

```bash
# Arrêter les conteneurs
docker compose down

# Supprimer le volume de la base de données
docker volume rm cyber-hoot_db_data

# Redémarrer (la base sera recréée automatiquement)
docker compose up --build
```

### Structure de la base de données

- `data/init/01-schema.sql` - Schéma de la base de données
- `data/init/02-seed-data.sql` - Données de test pour le développement

Ces fichiers sont automatiquement exécutés lors de la première initialisation du conteneur MySQL.
