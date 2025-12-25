from flask import Flask

from app.extensions.mongo import mongo
from app.extensions.jwt import jwt
from app.extensions.cors import cors
from app.routes import register_blueprints


def create_app(config_object):
    app = Flask(__name__)
    app.config.from_object(config_object)

    # init extensions
    mongo.init_app(app)
    jwt.init_app(app)
    cors.init_app(
        app,
        origins=app.config.get("CORS_ORIGINS"),
        supports_credentials=app.config.get("CORS_SUPPORTS_CREDENTIALS", False),
    )

    # register routes
    register_blueprints(app)

    # health check
    @app.route("/health", methods=["GET"])
    def health():
        return {"status": "ok"}, 200

    return app
