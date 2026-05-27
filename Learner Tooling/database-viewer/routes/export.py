"""Routes for exporting collection data.

Provides endpoints for downloading collection chunks
as CSV or JSON files with optional filtering.
"""

from flask import Blueprint, request, jsonify, Response

from services.export_service import ExportService

export_bp = Blueprint("export", __name__)

_export_service = None


def _get_export_service() -> ExportService:
    """Lazy-initialize the export service."""
    global _export_service
    if _export_service is None:
        _export_service = ExportService()
    return _export_service


@export_bp.route("/api/export/<collection_name>")
def export_collection(collection_name: str):
    """Export collection chunks as a downloadable file.

    Query parameters:
        format: "csv" or "json" (default: "json")
        path: optional file path filter
        type: optional chunk type filter

    Returns:
        File download with the exported data.
    """
    fmt = request.args.get("format", "json")
    path_filter = request.args.get("path")
    type_filter = request.args.get("type")

    try:
        service = _get_export_service()
        result = service.export_collection(
            collection_name=collection_name,
            fmt=fmt,
            path_filter=path_filter,
            type_filter=type_filter,
        )

        return Response(
            result.data,
            mimetype=result.content_type,
            headers={
                "Content-Disposition": f"attachment; filename={result.filename}",
                "X-Chunk-Count": str(result.chunk_count),
            },
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
