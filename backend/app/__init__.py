import os

from flask import Flask
from flask_cors import CORS

from app.database import initialize_database
from app.routes import requests_blueprint


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        DATABASE=os.path.join(os.path.dirname(os.path.dirname(__file__)), "requests.db"),
    )

    if test_config:
        app.config.update(test_config)

    # Permite que Vite, en su puerto local, consuma la API durante el desarrollo.
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    initialize_database(app)
    app.register_blueprint(requests_blueprint, url_prefix="/api/requests")
    return app