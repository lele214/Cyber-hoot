# Fichier d'initialisation de l'application Flask
# Ce fichier configure et assemble tous les composants de l'application

# Import de Flask pour créer l'application web
from flask import Flask
# Import de la fonction pour initialiser la base de données
from app.database import init_db


# Fonction principale qui crée et configure l'application Flask
def create_app():
    # Création de l'instance Flask
    app = Flask(__name__)

    # Import de la configuration de l'application (clés secrètes, paramètres DB, etc.)
    from app.config import Config

    # Application de la configuration à l'application Flask
    app.config.from_object(Config)

    # Initialisation de la base de données avec l'application
    init_db(app)

    # Import des différents blueprints (modules de routes)
    from app.routes.auth import auth_bp
    from app.routes.main_routes import main_bp
    from app.routes.profile import profile_bp

    # Enregistrement des blueprints dans l'application
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)

    # Retourne l'application configurée et prête à être lancée
    return app
