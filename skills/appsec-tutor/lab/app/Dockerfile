# VULN: old, full-fat base image (many OS CVEs), runs as root, no healthcheck
FROM python:3.8

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .

EXPOSE 5000
CMD ["python", "app.py"]
