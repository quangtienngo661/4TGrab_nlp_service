from flask import Flask, request, jsonify
import json
from intelligent_nlp_model import IntelligentFoodRecommender

# Tạo Flask app
app = Flask(__name__)

# Initialize intelligent recommender
recommender = None

# Tải dữ liệu món ăn
def load_dishes():
    with open('data/dishes.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def initialize_app():
    global recommender
    print("🚀 Initializing intelligent model...")
    recommender = IntelligentFoodRecommender()
    print("✅ Model ready!")

dishes = load_dishes()

# API tìm kiếm - SAME ENDPOINT, SMARTER LOGIC
@app.route('/search', methods=['POST']) # <--- CHANGED FROM GET TO POST
def search():
    data = request.json
    query_text = data.get("query")
    if not query_text:
        return jsonify({"error": "Missing 'query' parameter"}), 400

    try:
        # Use intelligent search instead of simple keyword matching
        recommendations = recommender.intelligent_search(query_text, dishes)

        # Extract just the dish data (same format as before)
        results = []
        for rec in recommendations:
            dish = rec["dish"]
            # Return the complete dish object with all original fields
            results.append({
                "categoryName": dish["categoryName"],
                "description": dish["description"],
                "imageUrl": dish["imageUrl"],
                "isDeleted": dish["isDeleted"],
                "isPopular": dish["isPopular"],
                "name": dish["name"],
                "price": dish["price"],
                "star": dish["star"],
                "time": dish["time"],
                "cuisine_type": dish["cuisine_type"],
                "dish_characteristics": dish["dish_characteristics"],
                "main_ingredients": dish["main_ingredients"],
                "__collections__": dish.get("__collections__", {})
            })

        # Return in your original format
        return jsonify({
            "query": query_text,
            "result": results
        })

    except Exception as e:
        print(f"Error in /search: {e}") # Added endpoint name for clarity
        import traceback
        traceback.print_exc()
        # Fallback to original method if intelligent model fails
        from nlp_model import analyze_query, search_dishes
        keywords = analyze_query(query_text)
        results = search_dishes(keywords, dishes)
        # Ensure the fallback also returns a proper response, even if empty
        return jsonify({"query": query_text, "result": results}), 500 # Changed status to 500 for error fallback

# Optional: Add new intelligent endpoint while keeping original
@app.route('/smart-search', methods=['POST']) # <--- CHANGED FROM GET TO POST
def smart_search():
    """Enhanced endpoint with reasoning and scores"""
    data = request.json
    query_text = data.get("query")
    if not query_text:
        return jsonify({"error": "Missing 'query' parameter"}), 400

    try:
        # Get emotional context
        emotional_context = recommender.analyze_emotional_context(query_text)

        # Get intelligent recommendations
        recommendations = recommender.intelligent_search(query_text, dishes)

        # Format with additional intelligence data
        enhanced_results = []
        for rec in recommendations:
            dish = rec["dish"]
            enhanced_results.append({
                "dish": {
                    "categoryName": dish["categoryName"],
                    "description": dish["description"],
                    "imageUrl": dish["imageUrl"],
                    "isDeleted": dish["isDeleted"],
                    "isPopular": dish["isPopular"],
                    "name": dish["name"],
                    "price": dish["price"],
                    "star": dish["star"],
                    "time": dish["time"],
                    "cuisine_type": dish["cuisine_type"],
                    "dish_characteristics": dish["dish_characteristics"],
                    "main_ingredients": dish["main_ingredients"],
                    "__collections__": dish.get("__collections__", {})
                },
                "confidence_score": float(rec["score"]),
                "reasoning": rec["reasoning"],
                "similarity": float(rec["similarity"])
            })

        return jsonify({
            "query": query_text,
            "emotional_analysis": emotional_context,
            "result": enhanced_results,
            "total_found": len(recommendations)
        })

    except Exception as e:
        print(f"Error in smart_search: {e}") # Added endpoint name for clarity
        import traceback
        traceback.print_exc() # Print full traceback for debugging
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    initialize_app()
    print("🌟 Starting intelligent food search API...")
    app.run(debug=True, host="0.0.0.0", port=5000)