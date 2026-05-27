"""Routes for embedding space visualization.

Provides API endpoints for generating 2D scatter plots
of high-dimensional embedding vectors using PCA or
random projection dimensionality reduction.
"""

from flask import Blueprint, request, jsonify

from services.chroma_client import get_chroma_client
from services.visualization_service import (
    VisualizationService,
    ReductionMethod,
    ColorScheme,
    get_reducer,
)

visualizer_bp = Blueprint("visualizer", __name__)


@visualizer_bp.route("/api/visualizer/points", methods=["POST"])
def get_point_cloud():
    """Generate a 2D point cloud from collection embeddings.

    Request JSON:
        collection: str - collection name
        method: str - "pca" or "random_projection" (default: "pca")
        color_by: str - "file", "type", or "symbol" (default: "file")
        max_points: int - maximum points to plot (default: 200)

    Returns:
        PointCloud as JSON with 2D coordinates and metadata.
    """
    data = request.get_json(force=True)
    collection_name = data.get("collection")

    if not collection_name:
        return jsonify({"error": "collection is required"}), 400

    # Parse reduction method
    method_str = data.get("method", "pca").lower()
    method_map = {
        "pca": ReductionMethod.PCA,
        "random_projection": ReductionMethod.RANDOM_PROJECTION,
    }
    method = method_map.get(method_str, ReductionMethod.PCA)

    # Parse color scheme
    color_str = data.get("color_by", "file").lower()
    color_map = {
        "file": ColorScheme.BY_FILE,
        "type": ColorScheme.BY_TYPE,
        "symbol": ColorScheme.BY_SYMBOL,
    }
    color_by = color_map.get(color_str, ColorScheme.BY_FILE)

    max_points = min(int(data.get("max_points", 200)), 500)

    try:
        manager = get_chroma_client()
        collection = manager.get_existing_collection(collection_name)
        if collection is None:
            return jsonify({"error": f"Collection not found: {collection_name}"}), 404

        reducer = get_reducer(method)
        service = VisualizationService(reducer=reducer)
        cloud = service.generate_point_cloud(
            collection=collection,
            color_by=color_by,
            max_points=max_points,
        )

        return jsonify(cloud.to_dict())

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@visualizer_bp.route("/api/visualizer/chunks", methods=["POST"])
def get_chunks_by_ids():
    """Fetch code and metadata for specific chunk IDs.

    Request JSON:
        collection: str - collection name
        chunk_ids: list[str] - one or more chunk IDs

    Returns:
        List of chunks with id, code, path, chunk_type, symbol.
    """
    data = request.get_json(force=True)
    collection_name = data.get("collection")
    chunk_ids = data.get("chunk_ids", [])

    if not collection_name or not chunk_ids:
        return jsonify({"error": "collection and chunk_ids are required"}), 400

    try:
        manager = get_chroma_client()
        collection = manager.get_existing_collection(collection_name)
        if collection is None:
            return jsonify({"error": f"Collection not found: {collection_name}"}), 404

        result = collection.get(ids=chunk_ids, include=["documents", "metadatas"])

        chunks = []
        for i, chunk_id in enumerate(result["ids"]):
            meta = result["metadatas"][i]
            chunks.append({
                "id": chunk_id,
                "code": result["documents"][i],
                "path": meta.get("path", "unknown"),
                "chunk_type": meta.get("chunk_type", "unknown"),
                "symbol": meta.get("symbol", ""),
            })

        return jsonify({"chunks": chunks})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
