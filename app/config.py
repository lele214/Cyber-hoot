import os


# Dossier secrets/ local (dev), équivalent de /run/secrets/ en Docker
_LOCAL_SECRETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "secrets")


def get_secret(env_var, secret_name, default=""):
    """Priorité : /run/secrets/ (Docker prod) > secrets/ local (dev) > variable d'environnement > default."""
    for secrets_dir in ("/run/secrets", _LOCAL_SECRETS_DIR):
        secret_path = os.path.join(secrets_dir, secret_name)
        if os.path.exists(secret_path):
            with open(secret_path, "r") as f:
                return f.read().strip()
    return os.getenv(env_var, default)


class Config:
    # ATTENTION : créer un fichier dans "secret/" avec la clé
    SECRET_KEY = os.getenv("SECRET_KEY", "cle_secrete_a_changer_en_production")

    # --- Upload de médias (images pour les quiz) ---
    # Dossier HORS de static/ pour ne pas être accessible publiquement
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 Mo max par fichier
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

    # --- VirusTotal API ---
    VIRUSTOTAL_API_KEY = get_secret("VIRUSTOTAL_API_KEY", "api_key")

    # --- Flask-Mail (SMTP) ---
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "false").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = get_secret("MAIL_PASSWORD", "mail_password")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", MAIL_USERNAME)

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


class TestingConfig(Config):
    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ECHO = False
    SECRET_KEY = "test-secret-key"
    VIRUSTOTAL_API_KEY = ""
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test", "uploads")


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
