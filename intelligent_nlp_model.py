from transformers import pipeline, AutoTokenizer, AutoModel
import torch
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import json

class IntelligentFoodRecommender:
    def __init__(self):
        # Load pre-trained models
        self.sentiment_analyzer = pipeline("sentiment-analysis")
        self.text_generator = pipeline("text-generation", model="gpt2", max_length=50)
        
        # For semantic similarity
        self.tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
        self.model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
        
        # Mood to food mapping (this is where the intelligence begins)
        self.mood_food_mapping = {
            "stressed": ["comfort food", "warm soup", "chocolate", "tea", "calming herbs"],
            "energetic": ["spicy food", "citrus", "protein rich", "fresh salads", "coffee"],
            "sad": ["comfort food", "sweet treats", "warm dishes", "chocolate", "ice cream"],
            "happy": ["light meals", "fresh ingredients", "colorful dishes", "celebration food"],
            "tired": ["energy boosting", "protein", "caffeine", "nuts", "fruits"],
            "anxious": ["calming foods", "herbal tea", "light meals", "avoiding caffeine"],
            "jumpy": ["calming foods", "magnesium rich", "avoiding stimulants", "herbal remedies"],
            "romantic": ["wine pairing", "elegant dishes", "aphrodisiac foods", "intimate dining"],
            "nostalgic": ["traditional dishes", "childhood favorites", "classic recipes", "comfort food"]
        }
        
        # Emotional keywords to detect
        self.emotional_keywords = {
            "stress": ["stressed", "overwhelmed", "pressure", "tense", "anxious"],
            "energy": ["energetic", "pumped", "active", "workout", "gym", "tired", "sleepy"],
            "mood": ["sad", "down", "depressed", "happy", "excited", "celebration"],
            "physical": ["jumpy", "restless", "can't sit still", "fidgety", "hyperactive"],
            "comfort": ["need comfort", "cozy", "warm", "hug", "security"]
        }

    def get_embeddings(self, text):
        """Get semantic embeddings for text"""
        inputs = self.tokenizer(text, return_tensors='pt', truncation=True, padding=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).numpy()

    def analyze_emotional_context(self, query):
        """Analyze the emotional context of the query"""
        query_lower = query.lower()
        detected_emotions = []
        
        # Check for emotional keywords
        for emotion, keywords in self.emotional_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                detected_emotions.append(emotion)
        
        # Use sentiment analysis
        sentiment = self.sentiment_analyzer(query)[0]
        
        return {
            "emotions": detected_emotions,
            "sentiment": sentiment,
            "confidence": sentiment['score']
        }

    def generate_contextual_keywords(self, query, emotional_context):
        """Generate intelligent keywords based on context"""
        base_keywords = []
        
        # Extract direct food-related words
        food_words = ["food", "dish", "meal", "eat", "hungry", "craving", "want", "need"]
        words = query.lower().split()
        direct_food_keywords = [word for word in words if word not in ["i", "am", "feel", "feeling", "like", "want", "need"]]
        
        # Add emotional context keywords
        for emotion in emotional_context["emotions"]:
            if emotion in ["stress", "comfort"]:
                base_keywords.extend(self.mood_food_mapping.get("stressed", []))
            elif emotion == "energy":
                if "tired" in query.lower() or "sleepy" in query.lower():
                    base_keywords.extend(self.mood_food_mapping.get("tired", []))
                else:
                    base_keywords.extend(self.mood_food_mapping.get("energetic", []))
            elif emotion == "physical":
                base_keywords.extend(self.mood_food_mapping.get("jumpy", []))
        
        # If sentiment is negative, add comfort food
        if emotional_context["sentiment"]["label"] == "NEGATIVE":
            base_keywords.extend(self.mood_food_mapping.get("sad", []))
        
        # Combine and deduplicate
        all_keywords = list(set(direct_food_keywords + base_keywords))
        
        return all_keywords

    def intelligent_search(self, query, dishes):
        """Perform intelligent search with reasoning"""
        print(f"🧠 Analyzing query: '{query}'")
        
        # Step 1: Analyze emotional context
        emotional_context = self.analyze_emotional_context(query)
        print(f"📊 Emotional analysis: {emotional_context}")
        
        # Step 2: Generate contextual keywords
        keywords = self.generate_contextual_keywords(query, emotional_context)
        print(f"🔍 Generated keywords: {keywords}")
        
        # Step 3: Semantic similarity search
        query_embedding = self.get_embeddings(query)
        
        scored_dishes = []
        for dish_id, dish_data in dishes.items():
            # Create dish description for embedding
            dish_text = f"{dish_data['name']} {dish_data['description']} {dish_data['categoryName']} {' '.join(dish_data['main_ingredients'])}"
            dish_embedding = self.get_embeddings(dish_text)
            
            # Calculate semantic similarity
            similarity = cosine_similarity(query_embedding, dish_embedding)[0][0]
            
            # Keyword matching score
            keyword_score = 0
            for keyword in keywords:
                if any(keyword.lower() in field.lower() for field in [
                    dish_data["name"], 
                    dish_data["description"], 
                    dish_data["categoryName"],
                    " ".join(dish_data["main_ingredients"]),
                    " ".join(dish_data["dish_characteristics"])
                ]):
                    keyword_score += 1
            
            # Combined score
            total_score = (similarity * 0.6) + (keyword_score * 0.4)
            
            scored_dishes.append({
                "dish": dish_data,
                "score": total_score,
                "similarity": similarity,
                "keyword_matches": keyword_score,
                "reasoning": f"Semantic similarity: {similarity:.3f}, Keyword matches: {keyword_score}"
            })
        
        # Sort by score
        scored_dishes.sort(key=lambda x: x["score"], reverse=True)
        
        return scored_dishes[:5]  # Return top 5

    def explain_recommendation(self, query, recommendations, emotional_context):
        """Generate explanation for recommendations"""
        explanation = f"Based on your query '{query}', I detected that you might be feeling "
        
        if emotional_context["emotions"]:
            explanation += f"{', '.join(emotional_context['emotions'])}. "
        
        if emotional_context["sentiment"]["label"] == "NEGATIVE":
            explanation += "Since you seem to need some comfort, I'm recommending foods that can help boost your mood. "
        elif "jumpy" in query.lower():
            explanation += "Since you're feeling jumpy, I'm suggesting calming foods that might help you relax. "
        
        explanation += f"Here are my top recommendations with reasoning:"
        
        return explanation

# Test function
def test_intelligent_model():
    recommender = IntelligentFoodRecommender()
    
    # Load dishes
    with open('data/dishes.json', 'r') as f:
        dishes = json.load(f)
    
    print("=== Intelligent Food Recommender ===")
    print("Try queries like:")
    print("- 'I feel jumpy and restless'")
    print("- 'I'm stressed and need comfort food'")
    print("- 'I'm tired and need energy'")
    print("- 'I want something to celebrate'")
    print("-" * 50)
    
    while True:
        query = input("\nWhat are you in the mood for? (or 'quit'): ")
        if query.lower() == 'quit':
            break
        
        try:
            # Get emotional context
            emotional_context = recommender.analyze_emotional_context(query)
            
            # Get recommendations
            recommendations = recommender.intelligent_search(query, dishes)
            
            # Explain reasoning
            explanation = recommender.explain_recommendation(query, recommendations, emotional_context)
            print(f"\n💡 {explanation}")
            
            # Show top recommendations
            print(f"\n🍽️ Top Recommendations:")
            for i, rec in enumerate(recommendations[:3], 1):
                dish = rec["dish"]
                print(f"\n{i}. {dish['name']} (Score: {rec['score']:.3f})")
                print(f"   Category: {dish['categoryName']}")
                print(f"   Reasoning: {rec['reasoning']}")
                print(f"   Description: {dish['description'][:100]}...")
        
        except Exception as e:
            print(f"Error: {e}")
            print("Make sure you have transformers installed: pip install transformers torch scikit-learn")

if __name__ == "__main__":
    test_intelligent_model()