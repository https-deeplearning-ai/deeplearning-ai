"""Live regex tester routes."""

from flask import Blueprint, request, jsonify

from utils.regex_engine import RegexTester
from services.chroma_client import get_chroma_client

regex_tester_bp = Blueprint("regex_tester", __name__)

_regex_tester = None


def _get_regex_tester():
    global _regex_tester
    if _regex_tester is None:
        _regex_tester = RegexTester()
    return _regex_tester


@regex_tester_bp.route("/api/regex/test", methods=["POST"])
def api_regex_test():
    """API: Test a regex pattern against provided text or a collection chunk."""
    data = request.get_json()
    pattern = data.get("pattern", "")
    text = data.get("text", "")
    chunk_id = data.get("chunk_id", "")
    collection_name = data.get("collection", "")

    if not pattern:
        return jsonify({"error": "Pattern is required"}), 400

    # If chunk_id provided, fetch text from collection
    if chunk_id and collection_name:
        manager = get_chroma_client()
        collection = manager.get_existing_collection(collection_name)
        if collection is None:
            return jsonify({"error": f"Collection not found: {collection_name}"}), 404

        result = collection.get(ids=[chunk_id], include=["documents"])
        if result["documents"]:
            text = result["documents"][0]

    if not text:
        return jsonify({"error": "No text to test against"}), 400

    tester = _get_regex_tester()
    analysis = tester.full_analysis(pattern, text)

    return jsonify(analysis)


@regex_tester_bp.route("/api/regex/sample", methods=["GET"])
def api_regex_sample():
    """API: Get a sample chunk from a collection for regex testing."""
    collection_name = request.args.get("collection", "")
    if not collection_name:
        return jsonify({"error": "Collection name required"}), 400

    manager = get_chroma_client()
    collection = manager.get_existing_collection(collection_name)
    if collection is None:
        return jsonify({"error": f"Collection not found: {collection_name}"}), 404

    # Get a few chunks to pick from
    result = collection.get(
        limit=10,
        include=["documents", "metadatas"],
    )

    samples = []
    for i in range(len(result["ids"])):
        meta = result["metadatas"][i]
        samples.append({
            "id": result["ids"][i],
            "symbol": meta.get("symbol", ""),
            "path": meta.get("path", ""),
            "preview": result["documents"][i][:100] + "..."
                       if len(result["documents"][i]) > 100
                       else result["documents"][i],
            "text": result["documents"][i],
        })

    return jsonify({"samples": samples})
