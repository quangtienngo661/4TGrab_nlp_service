import requests
import json
import time

# API base URL
BASE_URL = "http://192.168.2.174:5000"
# test_api.py (NO CHANGES NEEDED from the version I provided in the previous answer)

def test_health_check():
    """
    Test if API is running by attempting a POST request to a known endpoint
    with an empty JSON body, expecting a 400 Bad Request for missing 'query'.
    """
    print("🔍 Testing API availability by attempting a POST to /smart-search...")
    try:
        # Send a POST request with an empty JSON body to trigger a 400 for missing 'query'
        # This confirms the server is up and processing JSON requests.
        response = requests.post(f"{BASE_URL}/smart-search", json={}) # Send an empty JSON object
        
        if response.status_code == 400:
            print(f"✅ API appears to be running! Received status {response.status_code} (expected for missing 'query').")
            return True
        else:
            print(f"❌ Health check failed: Unexpected status code {response.status_code}. Response: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Health check failed: Could not connect to the API at {BASE_URL}. Is app.py running?")
        return False
    except Exception as e:
        print(f"❌ An unexpected error occurred during health check: {e}")
        return False

def test_food_recommendation(query):
    """Test the smart-search endpoint with a POST request."""
    print(f"\n🍽️ Testing smart-search for query: '{query}'")

    try:
        payload = {
            "query": query
        }

        # Change to POST request as per app.py logic for receiving JSON data
        response = requests.post(f"{BASE_URL}/smart-search", json=payload)

        if response.status_code == 200:
            data = response.json()

            print(f"✅ Success! Found {data.get('total_found', 0)} recommendations.")
            print(f"📊 Emotional Analysis: {data.get('emotional_analysis', 'N/A')}")

            results = data.get('result', [])
            if results:
                print(f"\n🏆 Top {len(results)} Recommendations:")
                for i, rec in enumerate(results):
                    dish = rec.get('dish', {})
                    # Ensure 'confidence_score' is float before formatting
                    confidence_score = rec.get('confidence_score', 'N/A')
                    if isinstance(confidence_score, (int, float)):
                        confidence_score_formatted = f"{confidence_score:.2f}"
                    else:
                        confidence_score_formatted = str(confidence_score) # Keep as string if not numeric

                    print(f"\n{i + 1}. {dish.get('name', 'N/A')} (Score: {confidence_score_formatted})")
                    print(f"    Category: {dish.get('categoryName', 'N/A')}")
                    print(f"    Cuisine: {dish.get('cuisine_type', 'N/A')}")
                    print(f"    Reasoning: {rec.get('reasoning', 'N/A')}")
                    print(f"    Description: {dish.get('description', 'N/A')[:100]}...")
            else:
                print("No recommendations found for this query.")

        else:
            print(f"❌ Error {response.status_code}: {response.json()}")

    except requests.exceptions.ConnectionError:
        print(f"❌ Request failed: Could not connect to the API at {BASE_URL}. Ensure app.py is running.")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

def interactive_test():
    """Interactive testing mode"""
    print("\n" + "=" * 20)
    print("=== Interactive API Testing ===")
    print("=" * 20)

    while True:
        print("\nOptions:")
        print("1. Test food recommendation")
        print("2. Exit")

        choice = input("Choose option (1-2): ")

        if choice == "1":
            query = input("Enter your food query: ")
            test_food_recommendation(query)

        elif choice == "2":
            print("Goodbye!")
            break
        else:
            print("Invalid choice! Please enter 1 or 2.")

def main():
    print("🚀 Food Recommendation API Test Client")
    print("=" * 50)

    # Give the server a moment to start if it's just been launched
    print("Waiting a few seconds for the API to initialize...")
    time.sleep(5)

    # Test health check first
    if not test_health_check():
        print("❌ API is not running or not reachable! Please start your Flask application (`python app.py`) before running tests.")
        return

    # Pre-defined test cases
    test_queries = [
        "I feel jumpy and restless",
        "I'm stressed from work and need comfort food",
        "I'm tired and need something energizing",
        "I want something to celebrate with friends"
    ]

    print("\n🧪 Running predefined tests...")
    for query in test_queries:
        test_food_recommendation(query)
        print("-" * 30) # Separator for clarity

    # Interactive mode
    interactive_test()

if __name__ == "__main__":
    main()