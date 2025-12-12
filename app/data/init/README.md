# Scripts d'initialisation de la base de données

Ce dossier contient les scripts SQL qui sont automatiquement exécutés lors de la première initialisation du conteneur MySQL.

## Fichiers

- **01-schema.sql** : Crée la structure de la base de données (tables, contraintes, index)
- **02-seed-data.sql** : Insère les données de test pour le développement

## Fonctionnement

Les fichiers de ce dossier sont montés dans `/docker-entrypoint-initdb.d/` du conteneur MySQL. Ils sont exécutés dans l'ordre alphabétique **uniquement lors de la première initialisation** (quand le volume `db_data` est vide).

## Mise à jour des données de test

Si vous modifiez la base de données et souhaitez mettre à jour les données de test :

```bash
# Exporter uniquement les données (sans le schéma)
docker compose exec -T db mysqldump -u flaskuser -pflaskpassword cyberhoot --no-create-info --skip-triggers > data/init/02-seed-data.sql

# Nettoyer le fichier si nécessaire (supprimer les warnings)
```

## Réinitialisation complète

Pour réinitialiser la base de données avec les scripts d'initialisation :

```bash
docker compose down
docker volume rm cyber-hoot_db_data
docker compose up --build
```
