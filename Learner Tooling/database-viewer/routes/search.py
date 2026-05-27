"""Search routes for semantic and regex queries."""

from flask import Blueprint, render_template, request, jsonify

from services.search_service import SearchService
from services.chroma_client import get_chroma_client
from utils.validators import validate_search_query, validate_regex_pattern

search_bp = Blueprint("search", __name__)

_search_service = None


def _get_search_service():
    global _search_service
    if _search_service is None:
        _search_service = SearchService()
    return _search_service


@search_bp.route("/search")
def search_page():
    """Render the search page."""
    manager = get_chroma_client()
    collections = manager.list_collections()
    collection_names = [c.name for c in collections]
    return render_template("search.html",
                           collections=collection_names,
                           active_page="search")


@search_bp.route("/api/search/semantic", methods=["POST"])
def api_semantic_search():
    """API endpoint for semantic search."""
    data = request.get_json()
    query = data.get("query", "")
    collection_name = data.get("collection", "")
    n_results = data.get("n_results", 10)
    filters = data.get("filters", {})

    is_valid, error = validate_search_query(query)
    if not is_valid:
        return jsonify({"error": error}), 400

    manager = get_chroma_client()
    collection = manager.get_existing_collection(collection_name)
    if collection is None:
        return jsonify({"error": f"Collection not found: {collection_name}"}), 404

    result_set = _get_search_service().semantic_search(
        collection, query, n_results=n_results, filters=filters
    )

    return jsonify({
        "results": result_set.to_dict_list(),
        "query": result_set.query,
        "total": len(result_set),
        "time_ms": round(result_set.total_time_ms, 1),
        "collection": collection_name,
    })


@search_bp.route("/api/search/regex", methods=["POST"])
def api_regex_search():
    """API endpoint for regex search."""
    data = request.get_json()
    pattern = data.get("pattern", "")
    collection_name = data.get("collection", "")
    n_results = data.get("n_results", 50)

    is_valid, error = validate_regex_pattern(pattern)
    if not is_valid:
        return jsonify({"error": error}), 400

    manager = get_chroma_client()
    collection = manager.get_existing_collection(collection_name)
    if collection is None:
        return jsonify({"error": f"Collection not found: {collection_name}"}), 404

    result_set = _get_search_service().regex_search(
        collection, pattern, n_results=n_results
    )

    return jsonify({
        "results": result_set.to_dict_list(),
        "pattern": result_set.query,
        "total": len(result_set),
        "time_ms": round(result_set.total_time_ms, 1),
        "collection": collection_name,
    })
