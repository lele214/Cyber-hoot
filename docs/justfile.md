# justfile — Command runner du projet

## Qu'est-ce que `just` ?

`just` est un **command runner** : il centralise toutes les commandes courantes du projet dans un fichier (`justfile`) versionné avec le code. L'objectif est de ne plus avoir à mémoriser des commandes longues et répétitives.

```bash
# Sans just :
docker compose exec app alembic revision --autogenerate -m "add column xyz"

# Avec just :
just migrate-new "add column xyz"
```

`just` est une alternative moderne à `make`, écrite en Rust. Contrairement à `make` qui a été conçu pour la compilation C, `just` est fait exclusivement pour lancer des commandes — sa syntaxe est plus claire et il fonctionne de manière identique sur Windows, Linux et macOS.

---

## Pourquoi `just` plutôt que `make` pour Cyber-hoot ?

| Critère | make | just |
|---------|------|------|
| Windows (sans WSL) | ❌ Non disponible nativement | ✅ Fonctionne |
| Linux | ✅ Préinstallé | Installation simple |
| Chargement du `.env` | ❌ Manuel | ✅ Automatique (`set dotenv-load`) |
| Arguments natifs | ❌ Syntaxe lourde (`NAME=val`) | ✅ `just migrate-new "nom"` |
| Erreur si commande échoue | ❌ Continue par défaut | ✅ S'arrête automatiquement |

Le projet tourne sous Docker sur Windows et Linux — `just` garantit que tout le monde utilise les mêmes commandes sans friction.

---

## Installation

**Windows** (dans Git Bash) :
```bash
mkdir -p ~/bin
curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to ~/bin
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

**Linux / macOS** :
```bash
curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to ~/.local/bin
```

Vérifier l'installation :
```bash
just --version
```

---

## Utilisation

```bash
# Voir toutes les commandes disponibles
just --list

# Lancer une commande
just <nom_de_la_commande>

# Lancer une commande avec un argument
just migrate-new "description de la migration"
```

---

## Commandes disponibles

### Application

| Commande | Description |
|----------|-------------|
| `just dev` | Démarre l'application au premier plan (logs visibles) |
| `just start` | Démarre en arrière-plan |
| `just stop` | Arrête tous les conteneurs |
| `just build` | Rebuild les images Docker et redémarre |
| `just build-detach` | Rebuild en arrière-plan |
| `just logs` | Affiche les logs de l'app en temps réel |
| `just logs-all` | Affiche les logs de tous les services |
| `just shell` | Ouvre un shell dans le conteneur app |
| `just status` | Affiche l'état des conteneurs |

### Base de données

| Commande | Description |
|----------|-------------|
| `just db-shell` | Ouvre un shell MySQL dans le conteneur db |
| `just db-reset` | ⚠️ Remet la DB à zéro (supprime toutes les données) |

> `db-reset` supprime le volume Docker `cyber-hoot_db_data` et recrée les conteneurs. La DB repart du schéma initial (`database/db_schemaV3-3.sql`) et des données de test (`test/seed_data.sql`).

### Migrations Alembic

| Commande | Description |
|----------|-------------|
| `just migrate-status` | Affiche la version actuelle et l'historique |
| `just migrate` | Applique toutes les migrations en attente |
| `just migrate-new "nom"` | Crée une migration autogénérée depuis les modèles |
| `just migrate-down` | Annule la dernière migration |
| `just migrate-init` | Initialise Alembic sur une DB existante (une seule fois) |

### Docker

| Commande | Description |
|----------|-------------|
| `just clean` | Supprime les conteneurs/images/volumes inutilisés |

---

## Workflow quotidien

### Démarrer le projet
```bash
just dev        # avec logs visibles
# ou
just start      # en arrière-plan
```

### Modifier la base de données
```bash
# 1. Modifier un modèle dans app/models/models.py
# 2. Générer la migration
just migrate-new "ajout colonne hint_text a question"
# 3. Vérifier le fichier généré dans alembic/versions/
# 4. Appliquer
just migrate
```

### Remettre la DB à zéro (données de test)
```bash
just db-reset
```

### Déboguer dans le conteneur
```bash
just shell       # shell dans l'app
just db-shell    # shell MySQL
```

---

## Mise en place initiale (nouveau clone du projet)

```bash
# 1. Installer just (voir section Installation)

# 2. Créer le fichier .env depuis l'exemple
cp .env.example .env
# Remplir les variables dans .env

# 3. Créer les fichiers secrets
echo "mot_de_passe_db" > secrets/db_password.txt
echo "mot_de_passe_root" > secrets/db_root_password.txt

# 4. Démarrer
just build
```
