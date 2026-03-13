# Cyber-hoot — Command runner
# Installation : https://github.com/casey/just#packages
# Usage        : just --list

set dotenv-load  # charge automatiquement le fichier .env

# Commande par défaut : affiche la liste des recettes disponibles
default:
    @just --list

# ─────────────────────────────────────────────
#  Application
# ─────────────────────────────────────────────

# Démarre l'application (dev)
dev:
    docker compose up

# Démarre l'application en arrière-plan
start:
    docker compose up -d

# Arrête l'application
stop:
    docker compose down

# Rebuild les images et redémarre
build:
    docker compose up --build

# Rebuild en arrière-plan
build-detach:
    docker compose up --build -d

# Affiche les logs de l'app en temps réel
logs:
    docker compose logs -f app

# Affiche les logs de tous les services
logs-all:
    docker compose logs -f

# Ouvre un shell dans le conteneur app
shell:
    docker compose exec app sh

# ─────────────────────────────────────────────
#  Base de données
# ─────────────────────────────────────────────

# Ouvre un shell MySQL
db-shell:
    docker compose exec db mysql -u${MYSQL_USER} -p${MYSQL_PASSWORD} ${MYSQL_DATABASE}

# Remet la DB à zéro (supprime les données et recrée depuis le schéma + seed)
# ⚠️  Supprime TOUTES les données !
db-reset:
    docker compose down
    docker volume rm cyber-hoot_db_data || true
    docker compose up -d

# ─────────────────────────────────────────────
#  Migrations Alembic
# ─────────────────────────────────────────────

# Affiche l'état des migrations
migrate-status:
    docker compose exec app alembic current
    docker compose exec app alembic history --verbose

# Applique toutes les migrations en attente
migrate:
    docker compose exec app alembic upgrade head

# Crée une nouvelle migration (autogénérée depuis les modèles)
# Usage : just migrate-new "description de la migration"
migrate-new description:
    docker compose exec app alembic revision --autogenerate -m "{{description}}"

# Annule la dernière migration
migrate-down:
    docker compose exec app alembic downgrade -1

# Initialise Alembic sur une DB existante (à faire une seule fois)
# Génère la migration baseline puis la marque comme déjà appliquée
migrate-init:
    docker compose exec app alembic revision --autogenerate -m "baseline_initial_schema"
    docker compose exec app alembic stamp head
    @echo "Alembic initialisé. La baseline est marquée comme appliquée."

# ─────────────────────────────────────────────
#  Badges
# ─────────────────────────────────────────────

# Initialise les badges prédéfinis et attribue rétroactivement aux utilisateurs existants
seed-badges:
    docker compose exec app flask seed-badges

# ─────────────────────────────────────────────
#  Tests unitaires
# ─────────────────────────────────────────────

# Lance tous les tests
test:
    python -m pytest -v

# Lance les tests en mode silencieux (résumé uniquement)
test-short:
    python -m pytest -q

# Lance un fichier ou un test spécifique
# Usage : just test-run test/test_quiz.py
#         just test-run test/test_quiz.py::test_quiz_creation_model
test-run target:
    python -m pytest -v {{target}}

# Lance les tests avec affichage des print()
test-debug:
    python -m pytest -v -s

# Lance les tests et s'arrête au premier échec
test-fail-fast:
    python -m pytest -v -x

# ─────────────────────────────────────────────
#  Docker utilitaires
# ─────────────────────────────────────────────

# Supprime les conteneurs, images et volumes inutilisés
clean:
    docker system prune -f

# Affiche le statut des conteneurs
status:
    docker compose ps
