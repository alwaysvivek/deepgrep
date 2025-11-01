# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

ENV PYTHONPATH=/app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data (WordNet) as required by the app
RUN python -c "import nltk; nltk.download('wordnet')"

RUN python -m spacy download en_core_web_md

# Copy the entire application code
COPY . .

# Expose the port the app runs on (matches default PORT in app.py)
EXPOSE 8000

# Command to run the application
CMD ["python", "deepgrep/web/app.py"]
