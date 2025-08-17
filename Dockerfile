FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files (since they're in root directory)
COPY . .

# Create database directory if it doesn't exist
RUN mkdir -p database

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=main.py
ENV FLASK_ENV=production

# Run the application (files are in root, not src/)
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:5000"]
