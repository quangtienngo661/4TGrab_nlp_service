from flask import Flask, request, jsonify
import json
from nlp_model import analyze_query, search_dishes

# Tạo Flask app
app = Flask(__name__)

# Tải dữ liệu món ăn
def load_dishes():
    with open('data/dishes.json', 'r', encoding='utf-8') as f:
        return json.load(f)

dishes = load_dishes()

# API tìm kiếm
@app.route('/search', methods=['GET'])
def search():
    data = request.json
    query_text = data.get("query")
    if not query_text:
        return jsonify({"error": "Missing 'query' parameter"}), 400

    # Phân tích query và tìm kiếm
    keywords = analyze_query(query_text)
    results = search_dishes(keywords, dishes)

    return jsonify({"query": query_text, "result": results})

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
