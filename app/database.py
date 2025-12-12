from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = app.config.get("SQLALCHEMY_DATABASE_URI")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = app.config.get("SQLALCHEMY_TRACK_MODIFICATIONS", False)
    app.config["SQLALCHEMY_ECHO"] = app.config.get("SQLALCHEMY_ECHO", False)

    db.init_app(app)

    return db
