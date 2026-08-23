#use python image
FROM python:3.10-slim

#set working directory
WORKDIR /app

#prevent .pyc files for neatness
ENV PYTHONDONTWRITEBYTECODE=1
#outputs logs immediately 
ENV PYTHONUNBUFFERED=1

#copy requirements and install dependencies
COPY ML_Service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#copy application files and ML model from build context root
COPY ML_Service/app.py .
COPY ML_Service/processed_data.csv .
COPY carbon_model.pkl ./carbon_model.pkl

#expose the port
EXPOSE 8000

#start the FastAPI, first app is app.py, second app is FastAPI object, host allows uvicorn to accept connections from outside the container and port tells uvicorn to run API on port 8000.
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]