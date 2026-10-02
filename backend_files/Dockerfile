
# Use a lightweight Python base image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the model file into the container
COPY superkart_model.joblib .

# Copy the application file into the container
COPY app.py .

# Expose the port on which the Flask app will run
EXPOSE 7860

# Set environment variable for the model directory
ENV MODEL_DIR="/app"

# Command to run the Flask application
CMD ["python", "app.py"]
