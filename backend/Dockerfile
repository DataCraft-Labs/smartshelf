FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy entire project directories
COPY backend /app/backend
COPY predictor /app/predictor

# Fix any potential README.md file issues
WORKDIR /app/predictor
RUN touch README.md

# Set up predictor package using direct pip install without editable mode
RUN pip install --no-cache-dir .

# Set up backend package
WORKDIR /app/backend
RUN pip install --no-cache-dir -e .

# Create directory for trained models
RUN mkdir -p app/models/trained

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 