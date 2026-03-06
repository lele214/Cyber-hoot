import os


def get_secret(env_var, secret_name, default=""):
    """Lit un secret depuis /run/secrets/ (Docker) ou une variable d'environnement (dev local)."""
    secret_path = f"/run/secrets/{secret_name}"
    if os.path.exists(secret_path):
        with open(secret_path, "r") as f:
            return f.read().strip()
    return os.getenv(env_var, default)


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "cle_secrete_a_changer_en_production")

    # --- Upload de médias (images pour les quiz) ---
    # Dossier HORS de static/ pour ne pas être accessible publiquement
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 Mo max par fichier
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

    MYSQL_USER = os.getenv("MYSQL_USER", "")
    MYSQL_PASSWORD = get_secret("MYSQL_PASSWORD", "db_password")
    MYSQL_HOST = os.getenv("MYSQL_HOST", "")
    MYSQL_PORT = os.getenv("MYSQL_PORT", "")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "")

    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.getenv("FLASK_ENV", "development") == "development"


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
