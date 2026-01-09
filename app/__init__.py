from flask import Flask
from app.database import init_db


def create_app():
    app = Flask(__name__)

    from app.config import Config

    app.config.from_object(Config)

    init_db(app)

    from app.routes.auth import auth_bp
    from app.routes.main_routes import main_bp
    from app.routes.profile import profile_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)

    return app
