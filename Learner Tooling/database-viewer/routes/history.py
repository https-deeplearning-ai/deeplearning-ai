"""Query history and bookmark routes."""

from flask import Blueprint, request, jsonify

from models.query_history import (
    HistoryManager, QueryRecord, Bookmark,
    SearchMode, BookmarkColor,
)

history_bp = Blueprint("history", __name__)

_history_manager = None


def _get_history_manager():
    global _history_manager
    if _history_manager is None:
        _history_manager = HistoryManager()
    return _history_manager


# ── Query History ────────────────────────────────────────────────

@history_bp.route("/api/history", methods=["GET"])
def api_get_history():
    """API: Get recent query history."""
    collection = request.args.get("collection", None)
    limit = request.args.get("limit", 20, type=int)

    records = _get_history_manager().get_history(
        collection=collection, limit=limit,
    )

    return jsonify({
        "history": [r.to_dict() for r in records],
        "total": len(records),
    })


@history_bp.route("/api/history", methods=["POST"])
def api_add_history():
    """API: Record a search query in history."""
    data = request.get_json()

    try:
        mode = SearchMode(data.get("mode", "semantic"))
    except ValueError:
        mode = SearchMode.SEMANTIC

    record = QueryRecord.create(
        query=data.get("query", ""),
        mode=mode,
        collection=data.get("collection", ""),
        result_count=data.get("result_count", 0),
        time_ms=data.get("time_ms", 0),
        filters=data.get("filters", {}),
    )

    _get_history_manager().add_query(record)

    return jsonify(record.to_dict())


@history_bp.route("/api/history", methods=["DELETE"])
def api_clear_history():
    """API: Clear query history."""
    collection = request.args.get("collection", None)
    removed = _get_history_manager().clear_history(collection=collection)
    return jsonify({"removed": removed})


@history_bp.route("/api/history/<query_id>", methods=["DELETE"])
def api_delete_query(query_id: str):
    """API: Delete a single history record."""
    success = _get_history_manager().delete_query(query_id)
    if success:
        return jsonify({"message": "Deleted"})
    return jsonify({"error": "Record not found"}), 404


# ── Bookmarks ────────────────────────────────────────────────────

@history_bp.route("/api/bookmarks", methods=["GET"])
def api_get_bookmarks():
    """API: Get bookmarks."""
    collection = request.args.get("collection", None)
    bookmarks = _get_history_manager().get_bookmarks(collection=collection)

    return jsonify({
        "bookmarks": [b.to_dict() for b in bookmarks],
        "total": len(bookmarks),
    })


@history_bp.route("/api/bookmarks", methods=["POST"])
def api_add_bookmark():
    """API: Bookmark a search result."""
    data = request.get_json()

    try:
        color = BookmarkColor(data.get("color", "yellow"))
    except ValueError:
        color = BookmarkColor.YELLOW

    bookmark = Bookmark.create(
        chunk_id=data.get("chunk_id", ""),
        collection=data.get("collection", ""),
        symbol=data.get("symbol", ""),
        path=data.get("path", ""),
        query=data.get("query", ""),
        score=data.get("score", 0),
        color=color,
        note=data.get("note", ""),
    )

    _get_history_manager().add_bookmark(bookmark)

    return jsonify(bookmark.to_dict())


@history_bp.route("/api/bookmarks/<bookmark_id>", methods=["DELETE"])
def api_delete_bookmark(bookmark_id: str):
    """API: Remove a bookmark."""
    success = _get_history_manager().delete_bookmark(bookmark_id)
    if success:
        return jsonify({"message": "Bookmark removed"})
    return jsonify({"error": "Bookmark not found"}), 404


@history_bp.route("/api/bookmarks/ids", methods=["GET"])
def api_bookmark_ids():
    """API: Get all bookmarked chunk IDs for a collection (fast lookup)."""
    collection = request.args.get("collection", "")
    ids = _get_history_manager().get_bookmark_ids(collection)
    return jsonify({"chunk_ids": list(ids)})
