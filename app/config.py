import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "cle_secrete_a_changer_en_production")

    MYSQL_USER = os.getenv("MYSQL_USER", "")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
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
