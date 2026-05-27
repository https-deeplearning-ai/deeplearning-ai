"""Chunk exploration and browsing routes."""

from flask import Blueprint, render_template, request, jsonify

from services.collection_service import CollectionService
from services.chroma_client import get_chroma_client
from utils.validators import validate_pagination

explorer_bp = Blueprint("explorer", __name__)

_collection_service = None


def _get_collection_service():
    global _collection_service
    if _collection_service is None:
        _collection_service = CollectionService()
    return _collection_service


@explorer_bp.route("/explorer/<name>")
def explorer_page(name: str):
    """Render the chunk browser for a collection."""
    stats = _get_collection_service().get_collection_stats(name)
    if stats is None:
        return render_template("explorer.html",
                               collection_name=name,
                               error="Collection not found",
                               active_page="explorer")
    return render_template("explorer.html",
                           collection_name=name,
                           stats=stats,
                           active_page="explorer")


@explorer_bp.route("/api/explorer/<name>/chunks")
def api_get_chunks(name: str):
    """API: Get paginated chunks with optional filters."""
    offset = request.args.get("offset", 0, type=int)
    limit = request.args.get("limit", 20, type=int)
    path_filter = request.args.get("path", None)
    type_filter = request.args.get("type", None)
    symbol_filter = request.args.get("symbol", None)

    offset, limit = validate_pagination(offset, limit)

    page = _get_collection_service().get_chunks_page(
        name, offset=offset, limit=limit,
        path_filter=path_filter,
        type_filter=type_filter,
        symbol_filter=symbol_filter,
    )

    return jsonify(page)
