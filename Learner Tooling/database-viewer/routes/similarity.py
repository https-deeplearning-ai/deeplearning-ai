"""Similarity computation routes."""

from flask import Blueprint, request, jsonify

from services.similarity_service import SimilarityService
from services.chroma_client import get_chroma_client

similarity_bp = Blueprint("similarity", __name__)

_similarity_service = None


def _get_similarity_service():
    global _similarity_service
    if _similarity_service is None:
        _similarity_service = SimilarityService()
    return _similarity_service


@similarity_bp.route("/api/similarity/matrix", methods=["POST"])
def api_similarity_matrix():
    """API: Compute pairwise similarity matrix for given chunk IDs."""
    data = request.get_json()
    chunk_ids = data.get("chunk_ids", [])
    collection_name = data.get("collection", "")

    if not chunk_ids or len(chunk_ids) < 2:
        return jsonify({"error": "At least 2 chunk IDs are required"}), 400

    if len(chunk_ids) > 30:
        return jsonify({"error": "Maximum 30 chunks for heatmap"}), 400

    manager = get_chroma_client()
    collection = manager.get_existing_collection(collection_name)
    if collection is None:
        return jsonify({"error": f"Collection not found: {collection_name}"}), 404

    matrix = _get_similarity_service().compute_matrix(collection, chunk_ids)

    return jsonify(matrix.to_dict())
