pip install --user spacy
pip install transformers torch scikit-learn sentence-transformers
pip install flask flask-cors requests
python -m spacy download en_core_web_sm

# To test the model directly:
python intelligent_nlp_model.py

# To test the api
python app.py
python test_api.py
# Might need to change the BASE_URL inside