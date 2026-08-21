FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY application_ml.py .
COPY processed_data.csv .

CMD ["python", "application_ml.py"]