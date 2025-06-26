import spacy

# Load the spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Analyze query to extract keywords
def analyze_query(query_text):
    """
    Process user query and extract keywords.
    """
    doc = nlp(query_text.lower())
    return [token.text for token in doc if not token.is_stop and not token.is_punct]

# Search for dishes in dataset
def search_dishes(keywords, dishes):
    """
    Search for matching dishes in the dataset using keywords.
    """
    matching_dishes = []

    for dish_data in dishes.items():
        # Combine all searchable fields into one string
        fields_to_search = [
            dish_data["categoryName"].lower(),
            dish_data["description"].lower(),
            dish_data["name"].lower(),
            dish_data["cuisine_type"].lower(),
            " ".join(dish_data["dish_characteristics"]).lower(),
            " ".join(dish_data["main_ingredients"]).lower()
        ]

        # Check if any keyword is found in any field
        if any(any(keyword in field for keyword in keywords) for field in fields_to_search):
            matching_dishes.append(dish_data)

    return matching_dishes