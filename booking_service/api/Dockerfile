FROM python:3.10-slim-buster

# Set the working directory
WORKDIR /booking_service

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY ./api/requirements.txt /booking_service/requirements.txt
RUN pip install --no-cache-dir -r /booking_service/requirements.txt

# Copy the source code
COPY ./api /booking_service

# Copy the entrypoint script
COPY ./api/entrypoint.sh /booking_service/entrypoint.sh

# Set execute permissions for the entrypoint script
RUN chmod +x /booking_service/entrypoint.sh

# Expose the port
EXPOSE 8000

# Set the entrypoint
ENTRYPOINT ["/bin/sh", "-c", "ls -l /booking_service/entrypoint.sh && /booking_service/entrypoint.sh"]
