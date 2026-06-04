"""Routes for the interactive tutorial and onboarding system.

Provides API endpoints to retrieve tutorial step data for
guided page tours. Each page can have its own tutorial
sequence that highlights UI elements and explains features.
"""

from flask import Blueprint, jsonify

from services.tutorial_service import TutorialManager

tutorial_bp = Blueprint("tutorial", __name__)

_tutorial_manager = None


def _get_tutorial_manager() -> TutorialManager:
    """Lazy-initialize the tutorial manager."""
    global _tutorial_manager
    if _tutorial_manager is None:
        _tutorial_manager = TutorialManager()
    return _tutorial_manager


@tutorial_bp.route("/api/tutorial/<page_name>")
def get_tutorial(page_name: str):
    """Get the tutorial sequence for a specific page.

    Returns the full tutorial definition including steps,
    selectors, positions, and completion messages.

    Args:
        page_name: The page identifier (e.g. 'dashboard', 'collection').

    Returns:
        TutorialSequence as JSON, or 404 if no tutorial exists.
    """
    manager = _get_tutorial_manager()
    tutorial = manager.get_tutorial(page_name)

    if tutorial is None:
        return jsonify({"error": f"No tutorial for page: {page_name}"}), 404

    return jsonify(tutorial.to_dict())


@tutorial_bp.route("/api/tutorials")
def list_tutorials():
    """List all available tutorials with metadata.

    Returns a summary of each available tutorial including
    the page name, title, and number of steps.
    """
    manager = _get_tutorial_manager()
    return jsonify({"tutorials": manager.list_available()})
