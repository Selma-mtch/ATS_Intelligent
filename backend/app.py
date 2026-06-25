from flask import Flask
from flask_cors import CORS
from config import FLASK_DEBUG, PORT, SECRET_KEY
from controllers.admin_controller import admin_bp
from controllers.auth_controller import auth_bp
from controllers.candidature_controller import candidature_bp
from controllers.cv_controller import cv_bp
from controllers.offre_controller import offre_bp
from database import init_db


def create_app():
    app = Flask(__name__)
    app.secret_key = SECRET_KEY

    CORS(app, supports_credentials=True)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(candidature_bp)
    app.register_blueprint(cv_bp)
    app.register_blueprint(offre_bp)

    @app.route("/")
    def health():
        return {
            "status": "ok",
            "message": "ATS Intelligent API en ligne",
        }

    return app


app = create_app()


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=PORT, debug=FLASK_DEBUG)
