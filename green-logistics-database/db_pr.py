import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv


# Load the .env file that is in the same folder as this db.py
env_path = Path(__file__).with_name(".env")
load_dotenv(dotenv_path=env_path, override=True)


def get_db_connection():
    host = os.getenv("POSTGRES_HOST", "localhost")

    print("Connecting to host:", host)

    return psycopg.connect(
        host=host,
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )