FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy requirements and install dependencies
COPY ML_Service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files and ML model from build context root
COPY ML_Service/app.py .
COPY ML_Service/processed_data.csv .
COPY carbon_model.pkl ./carbon_model.pkl

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
