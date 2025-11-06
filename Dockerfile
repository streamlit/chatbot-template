# Use the official Python image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install system dependencies
# - Tesseract for OCR
# - Cron for scheduled tasks
# - Git for Hugging Face integration
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    cron \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Make the startup script executable
RUN chmod +x /app/start.sh

# Expose the port FastAPI will run on
EXPOSE 7860

# Set the entrypoint to the startup script
CMD ["/app/start.sh"]
