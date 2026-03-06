import os
from flask import Flask
from dotenv import load_dotenv


def create_app(config_name=None):
    """Application Factory - crée et configure l'application Flask"""
    load_dotenv()

    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)

    # Charger la configuration
    from app.config import config
    app.config.from_object(config[config_name])

    # Initialiser les extensions
    from app.extensions import db
    db.init_app(app)

    # Enregistrer les blueprints
    from app.routes.main_routes import main_bp
    from app.routes.auth import auth_bp
    from app.routes.profile import profile_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)

    # Créer le dossier d'uploads s'il n'existe pas
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    return app
