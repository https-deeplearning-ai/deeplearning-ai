"""Collection management routes."""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash

from services.collection_service import CollectionService
from services.ingestion_service import IngestionService
from utils.validators import validate_collection_name, validate_directory_path

collections_bp = Blueprint("collections", __name__)

_collection_service = None
_ingestion_service = None


def _get_collection_service():
    global _collection_service
    if _collection_service is None:
        _collection_service = CollectionService()
    return _collection_service


def _get_ingestion_service():
    global _ingestion_service
    if _ingestion_service is None:
        _ingestion_service = IngestionService()
    return _ingestion_service


@collections_bp.route("/")
def index():
    """Dashboard: show all collections with stats."""
    collections = _get_collection_service().list_collections()
    return render_template("index.html",
                           collections=collections,
                           active_page="dashboard")


@collections_bp.route("/collection/<name>")
def collection_detail(name: str):
    """Show detailed stats for a single collection."""
    stats = _get_collection_service().get_collection_stats(name)
    if stats is None:
        flash(f"Collection '{name}' not found.", "danger")
        return redirect(url_for("collections.index"))
    return render_template("collection.html",
                           stats=stats,
                           active_page="collections")


@collections_bp.route("/api/collections", methods=["POST"])
def api_create_collection():
    """API: Create a new collection."""
    data = request.get_json()
    name = data.get("name", "")

    is_valid, error = validate_collection_name(name)
    if not is_valid:
        return jsonify({"error": error}), 400

    success = _get_collection_service().create_collection(name)
    if success:
        return jsonify({"message": f"Collection '{name}' created", "name": name})
    return jsonify({"error": "Failed to create collection"}), 500


@collections_bp.route("/api/collections/<name>", methods=["DELETE"])
def api_delete_collection(name: str):
    """API: Delete a collection."""
    success = _get_collection_service().delete_collection(name)
    if success:
        return jsonify({"message": f"Collection '{name}' deleted"})
    return jsonify({"error": f"Failed to delete '{name}'"}), 500


@collections_bp.route("/api/collections/<name>/ingest", methods=["POST"])
def api_ingest_directory(name: str):
    """API: Ingest a directory into a collection."""
    data = request.get_json()
    directory = data.get("directory", "")

    is_valid, error = validate_directory_path(directory)
    if not is_valid:
        return jsonify({"error": error}), 400

    progress = _get_ingestion_service().ingest_directory(directory, name)

    return jsonify({
        "message": "Ingestion complete",
        "progress": progress.to_dict(),
    })
