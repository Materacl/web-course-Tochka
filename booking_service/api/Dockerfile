FROM python:3.10-slim

# Set the working directory
WORKDIR /booking_service

# Install dependencies
COPY ./api/requirements.txt /booking_service/requirements.txt
RUN pip install --no-cache-dir -r /booking_service/requirements.txt

# Copy the source code
COPY ./api /booking_service

# Copy the entrypoint script
COPY ./api/entrypoint.sh /booking_service/entrypoint.sh

# Make the entrypoint script executable
RUN chmod +x /booking_service/entrypoint.sh

# Expose the port
EXPOSE 8000

# Set the entrypoint
ENTRYPOINT ["/booking_service/entrypoint.sh"]
