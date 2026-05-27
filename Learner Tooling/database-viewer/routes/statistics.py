"""Routes for code statistics and analytics.

Provides API endpoints for computing detailed code metrics
including line counts, construct detection, size distributions,
and per-file breakdowns for collection analysis.
"""

from flask import Blueprint, jsonify

from services.chroma_client import get_chroma_client
from services.statistics_service import StatisticsService

statistics_bp = Blueprint("statistics", __name__)

_statistics_service = None


def _get_statistics_service() -> StatisticsService:
    """Lazy-initialize the statistics service."""
    global _statistics_service
    if _statistics_service is None:
        _statistics_service = StatisticsService()
    return _statistics_service


@statistics_bp.route("/api/statistics/<collection_name>")
def get_statistics(collection_name: str):
    """Compute code statistics for a collection.

    Analyzes all chunks in the collection to produce metrics
    on code size, structure, constructs, and complexity.

    Returns:
        CollectionStatistics as JSON with overview, files,
        constructs, size distribution, and top symbols.
    """
    manager = get_chroma_client()
    collection = manager.get_existing_collection(collection_name)

    if collection is None:
        return jsonify({"error": f"Collection not found: {collection_name}"}), 404

    try:
        service = _get_statistics_service()
        statistics = service.compute_statistics(collection)
        return jsonify(statistics.to_dict())

    except Exception as e:
        return jsonify({"error": str(e)}), 500
