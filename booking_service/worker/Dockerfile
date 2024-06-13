# worker/Dockerfile
FROM python:3.10-slim-buster

WORKDIR /app

COPY ./worker/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY ./worker /app

CMD ["python", "worker.py"]
