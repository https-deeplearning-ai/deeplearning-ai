"""Route blueprints for the Flask application."""

from flask import Flask


def register_blueprints(app: Flask) -> None:
    """Register all route blueprints with the Flask app."""
    from routes.search import search_bp
    from routes.collections import collections_bp
    from routes.explorer import explorer_bp
    from routes.similarity import similarity_bp
    from routes.history import history_bp
    from routes.regex_tester import regex_tester_bp
    from routes.visualizer import visualizer_bp
    from routes.suggestions import suggestions_bp
    from routes.statistics import statistics_bp
    from routes.tutorial import tutorial_bp
    from routes.export import export_bp
    from routes.diff import diff_bp

    app.register_blueprint(search_bp)
    app.register_blueprint(collections_bp)
    app.register_blueprint(explorer_bp)
    app.register_blueprint(similarity_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(regex_tester_bp)
    app.register_blueprint(visualizer_bp)
    app.register_blueprint(suggestions_bp)
    app.register_blueprint(statistics_bp)
    app.register_blueprint(tutorial_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(diff_bp)
