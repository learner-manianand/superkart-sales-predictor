
import os
import pandas as pd
import joblib
from flask import Flask, request, jsonify

# Initialize Flask application
superkart_api = Flask(__name__)

# Define the path to the model file
MODEL_DIR = os.environ.get("MODEL_DIR", "/app") # default path when running in Docker
MODEL_PATH = os.path.join(MODEL_DIR, "superkart_model.joblib")

# Load the trained model
try:
    model = joblib.load(MODEL_PATH)
    print(f"Model loaded from {MODEL_PATH}")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

@superkart_api.route("/health", methods=["GET"])
def health():
    """Return service health"""
    return jsonify({"status": "healthy"})


@superkart_api.route("/v1/predict", methods=["POST"])
def predict():
    """Predicts sales for a single product entry."""
    if model is None:
        return jsonify({"error": "Model not loaded"}), 500

    try:
        # Get JSON data from the request body
        json_data = request.get_json(force=True)

        # Convert JSON data to DataFrame
        data_df = pd.DataFrame([json_data])

        # Make prediction
        prediction = model.predict(data_df)[0]

        return jsonify({"prediction": prediction}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@superkart_api.route("/v1/predictbatch", methods=["POST"])
def predict_batch():
    """Predicts sales for multiple product entries."""
    if model is None:
        return jsonify({"error": "Model not loaded"}), 500

    try:
        # Check if a file is uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file part in the request'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if file:
            # Read the CSV file into a pandas DataFrame
            data_df = pd.read_csv(file)

            # Make predictions
            predictions = model.predict(data_df)

            # Return predictions as JSON
            return jsonify({'predictions': predictions.tolist()}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    # Run the Flask app
    # The host is set to '0.0.0.0' to make the server accessible externally
    # The port is set to 7860 as defined in the docker-compose.yml
    superkart_api.run(host="0.0.0.0", port=7860)
