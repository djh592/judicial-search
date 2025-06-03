from flask import Flask, request, jsonify
from backend.config import (
    FLASK_DEBUG,
    FLASK_HOST,
    FLASK_PORT,
)
from backend.search.query import QueryParams
from backend.search.query_manager import get_query_manager

app = Flask(__name__)


@app.route("/api/query", methods=["POST"])
def create_query():
    data = request.get_json()
    user_query = data.get("user_query", {})
    params = QueryParams.from_dict(user_query)
    query_manager = get_query_manager()
    query_id = query_manager.create_query(params)
    total_results = query_manager.get_query(query_id)["total_results"]
    return jsonify({"query_id": query_id, "total_results": total_results})


@app.route("/api/query/<query_id>/results", methods=["GET"])
def get_query_results(query_id):
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 10))
    query_manager = get_query_manager()
    result = query_manager.get_results(query_id, page=page, page_size=page_size)
    if result is None:
        return jsonify({"error": "Query not found"}), 404
    # 字段名调整为 queryResults
    return jsonify(result)


@app.route("/api/query/<query_id>", methods=["GET"])
def get_query_meta(query_id):
    query_manager = get_query_manager()
    meta = query_manager.get_query(query_id)
    if meta is None:
        return jsonify({"error": "Query not found"}), 404
    return jsonify(meta)


@app.route("/api/query/<query_id>", methods=["PUT"])
def update_query(query_id):
    data = request.get_json()
    user_query = data.get("user_query", {})
    params = QueryParams.from_dict(user_query)
    query_manager = get_query_manager()
    updated_id = query_manager.update_query(query_id, params)
    if updated_id is None:
        return jsonify({"error": "Query not found"}), 404
    total_results = query_manager.get_query(updated_id)["total_results"]
    return jsonify({"query_id": updated_id, "total_results": total_results})


@app.route("/api/document/<ajid>", methods=["GET"])
def get_document_detail(ajid):
    query_manager = get_query_manager()
    doc = query_manager.get_document_by_ajid(ajid)
    if doc is None:
        return jsonify({"error": "Document not found"}), 404
    return jsonify(doc)


@app.route("/api/labels", methods=["GET"])
def get_all_labels():
    query_manager = get_query_manager()
    labels = query_manager.get_all_labels()
    return jsonify({"labels": labels})


@app.route("/api/suggest", methods=["GET"])
def suggest():
    prefix = request.args.get("q", "")
    if not prefix:
        return jsonify({"suggestions": []})
    query_manager = get_query_manager()
    # 支持 suggest 的字段列表
    suggest_fields = [
        "ajName",
        "fymc",
        "spry",
        "dsr",
        "labels",
        "ajjbqk",
        "cpfxgc",
        "pjjg",
        "qw",
        "writName",
    ]
    all_suggestions = set()
    for field in suggest_fields:
        try:
            suggestions = query_manager.suggest(field, prefix)
            all_suggestions.update(suggestions)
        except Exception:
            continue  # 某些字段没有suggest字段时跳过
    return jsonify({"suggestions": list(all_suggestions)})


if __name__ == "__main__":
    app.run(debug=FLASK_DEBUG, host=FLASK_HOST, port=FLASK_PORT)
