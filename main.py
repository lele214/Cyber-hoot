from flask import Flask
from database import init_db
from routes.auth import auth_bp
from routes.main_routes import main_bp

app = Flask(__name__)
app.secret_key = "cle_secrete_a_changer_en_production"

# Initialiser la base de données
init_db(app)

app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)

# Le reste des chemins sont dans les "routes"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
