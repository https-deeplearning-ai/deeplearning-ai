"""Flask application entry point for the ChromaDB Code Search UI."""

import os
import sys
import logging
from flask import Flask, jsonify
from dotenv import load_dotenv

# Ensure the app directory is on the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import get_config
from routes import register_blueprints


class ReverseProxied:
    """WSGI middleware that sets SCRIPT_NAME from an environment variable.

    When Flask runs behind a reverse proxy at a URL prefix (e.g. /flask/),
    this middleware tells Flask about the prefix so that url_for() generates
    correct URLs. Set SCRIPT_NAME=/flask in the environment to activate.
    """

    def __init__(self, app, script_name=""):
        self.app = app
        self.script_name = script_name

    def __call__(self, environ, start_response):
        if self.script_name:
            environ["SCRIPT_NAME"] = self.script_name
            path_info = environ.get("PATH_INFO", "")
            if path_info.startswith(self.script_name):
                environ["PATH_INFO"] = path_info[len(self.script_name):]
        return self.app(environ, start_response)


def create_app() -> Flask:
    """Application factory: create and configure the Flask app."""
    load_dotenv()
    config = get_config()

    app = Flask(__name__)
    app.secret_key = config.secret_key

    # Support running behind a reverse proxy with a URL prefix
    script_name = os.environ.get("SCRIPT_NAME", "")
    if script_name:
        app.wsgi_app = ReverseProxied(app.wsgi_app, script_name=script_name)

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if config.debug else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # Register all route blueprints
    register_blueprints(app)

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500

    app.logger.info(
        f"ChromaDB UI started in {config.environment.value} mode "
        f"on {config.host}:{config.port}"
    )

    return app


app = create_app()


if __name__ == "__main__":
    config = get_config()
    app.run(host=config.host, port=config.port, debug=config.debug)
