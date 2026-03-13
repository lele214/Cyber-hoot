import os
import sys
from logging.config import fileConfig

from sqlalchemy import pool
from alembic import context

# Ajouter la racine du projet au path Python pour pouvoir importer l'app Flask
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importer la factory Flask et l'instance db
from app import create_app
from app.extensions import db

# Importer tous les modèles pour qu'Alembic les détecte lors de l'autogenerate
import app.models.models  # noqa: F401

# Config Alembic
config = context.config

# Configurer le logging depuis alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Créer l'app Flask pour accéder à sa configuration
flask_app = create_app()

# Récupérer l'URL de la DB depuis la config Flask et l'injecter dans Alembic
with flask_app.app_context():
    config.set_main_option(
        "sqlalchemy.url",
        flask_app.config["SQLALCHEMY_DATABASE_URI"]
    )
    # Métadonnées des modèles SQLAlchemy — utilisées pour l'autogenerate
    target_metadata = db.metadata


def run_migrations_offline() -> None:
    """
    Mode offline : génère le SQL sans connexion réelle à la DB.
    Utile pour inspecter les migrations avant de les appliquer.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Mode online : applique les migrations avec une vraie connexion à la DB.
    C'est le mode utilisé normalement avec `alembic upgrade head`.
    """
    with flask_app.app_context():
        connectable = db.engine
        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                # Compare les types de colonnes pour détecter les changements
                compare_type=True,
            )
            with context.begin_transaction():
                context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
