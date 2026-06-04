"""Routes for smart query suggestions.

Provides an API endpoint that analyzes collection metadata
to generate contextual search query suggestions for both
semantic and regex search modes.
"""

from flask import Blueprint, jsonify

from services.chroma_client import get_chroma_client
from services.suggestion_service import SuggestionService

suggestions_bp = Blueprint("suggestions", __name__)

_suggestion_service = None


def _get_suggestion_service() -> SuggestionService:
    """Lazy-initialize the suggestion service."""
    global _suggestion_service
    if _suggestion_service is None:
        _suggestion_service = SuggestionService()
    return _suggestion_service


@suggestions_bp.route("/api/suggestions/<collection_name>")
def get_suggestions(collection_name: str):
    """Get smart query suggestions for a collection.

    Analyzes the collection's metadata (symbols, file paths,
    chunk types) to generate relevant search queries.

    Returns:
        SuggestionSet as JSON with categorized suggestions.
    """
    manager = get_chroma_client()
    collection = manager.get_existing_collection(collection_name)

    if collection is None:
        return jsonify({"error": f"Collection not found: {collection_name}"}), 404

    try:
        service = _get_suggestion_service()
        suggestion_set = service.get_suggestions(collection, max_suggestions=20)
        return jsonify(suggestion_set.to_dict())

    except Exception as e:
        return jsonify({"error": str(e)}), 500
