from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import numpy as np
import os 

app = Flask(__name__)
# Allow requests from any origin, which is fine for development
CORS(app) 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Definir las rutas completas para los archivos .joblib
MODEL_PATH = os.path.join(BASE_DIR, 'exoplanet_model.joblib')
ENCODER_PATH = os.path.join(BASE_DIR, 'label_encoder.joblib')
COLUMNS_PATH = os.path.join(BASE_DIR, 'feature_columns.joblib')

# Load the trained model, encoder, and feature columns
try:
    # Cargar usando la ruta completa
    model = joblib.load(MODEL_PATH)
    label_encoder = joblib.load(ENCODER_PATH)
    feature_columns = joblib.load(COLUMNS_PATH)
    print("Model and supporting files loaded successfully.")
except FileNotFoundError as e:
    print(f"CRITICAL: Model file not found: {e}. The '/predict' endpoint will not work.")
    print(f"Buscando en BASE_DIR: {BASE_DIR}") # Útil para depuración
    model = None
    label_encoder = None
    feature_columns = []

@app.route('/')
def status():
    """Returns the API status."""
    if model:
        return jsonify({
            'status': 'online',
            'message': 'Exoplanet prediction API is running.'
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'Model files not loaded. API is not functional.'
        }), 500


@app.route('/predict', methods=['POST'])
def predict():
    """Handles the prediction request."""
    if model is None or label_encoder is None:
        return jsonify({'error': 'Model not loaded. Cannot make predictions.'}), 500

    try:
        # Get data from the POST request's JSON body
        data = request.get_json()
        if data is None:
            return jsonify({'error': 'Invalid JSON input.'}), 400

        # Create a DataFrame from the input data
        # The react app will send a dictionary of {feature: value}
        input_df = pd.DataFrame([data])
        
        # Ensure the column order and presence is the same as during training
        # Fill missing columns with 0 (or a more appropriate default)
        for col in feature_columns:
            if col not in input_df.columns:
                input_df[col] = 0
        input_df = input_df[feature_columns]


        # Make prediction
        prediction_encoded = model.predict(input_df)
        
        # Decode the prediction to the original label
        prediction = label_encoder.inverse_transform(prediction_encoded)

        # Get prediction probabilities
        probabilities = model.predict_proba(input_df)
        class_probabilities = {cls: float(prob) for cls, prob in zip(label_encoder.classes_, probabilities[0])}

        # Return the result as JSON
        return jsonify({
            'prediction': prediction[0],
            'probabilities': class_probabilities
        })

    except Exception as e:
        return jsonify({'error': f'An error occurred during prediction: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)