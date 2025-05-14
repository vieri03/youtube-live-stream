# Use lightweight Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install required system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-traditional gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy wait-for script
COPY wait-for-kafka.sh /wait-for-kafka.sh
RUN chmod +x /wait-for-kafka.sh

# Copy requirements first to leverage caching
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the application
COPY . .

# Set entrypoint to wait for Kafka
ENTRYPOINT ["/wait-for-kafka.sh"]
CMD ["python", "producer.py"]
