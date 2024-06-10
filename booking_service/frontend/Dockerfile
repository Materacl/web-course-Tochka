FROM python:3.10-slim

# Set the working directory
WORKDIR /booking_service

# Install dependencies
COPY ./frontend/requirements.txt /booking_service/requirements.txt
RUN pip install --no-cache-dir -r /booking_service/requirements.txt

# Copy the source code
COPY ./frontend /booking_service

# Expose the port
EXPOSE 8001

# Run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
