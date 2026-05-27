"""Routes for comparing collections.

Provides an API endpoint for diffing two collections
to identify added, removed, and modified chunks.
"""

from flask import Blueprint, request, jsonify

from services.diff_service import DiffService

diff_bp = Blueprint("diff", __name__)

_diff_service = None


def _get_diff_service() -> DiffService:
    """Lazy-initialize the diff service."""
    global _diff_service
    if _diff_service is None:
        _diff_service = DiffService()
    return _diff_service


@diff_bp.route("/api/diff")
def diff_collections():
    """Compare two collections and return a diff report.

    Query parameters:
        source: name of the "before" collection (required)
        target: name of the "after" collection (required)
        modified: whether to detect modified chunks via similarity ("true"/"false", default "true")

    Returns:
        DiffReport as JSON with added, removed, modified, and unchanged counts.
    """
    source = request.args.get("source")
    target = request.args.get("target")

    if not source or not target:
        return jsonify({"error": "Both 'source' and 'target' query parameters are required"}), 400

    include_modified = request.args.get("modified", "true").lower() == "true"

    try:
        service = _get_diff_service()
        report = service.compare(source, target, include_modified=include_modified)
        return jsonify(report.to_dict())

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
