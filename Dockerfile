FROM python:3.11-slim

WORKDIR /app

# Install cron
RUN apt-get update && \
    apt-get install -y --no-install-recommends cron && \
    rm -rf /var/lib/apt/lists/*

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy pipeline script
COPY pipeline.py .

# Make sure output goes to stdout/stderr (cron normally emails output)
RUN touch /var/log/cron.log

# Start cron in foreground with logging
CMD ["cron", "-f"]