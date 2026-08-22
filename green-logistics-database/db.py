import os
from pathlib import Path
import psycopg
from dotenv import load_dotenv

# Load .env file if present (do not override system/container environment variables)
env_path = Path(__file__).with_name(".env")
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=False)

def get_db_connection():
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    dbname = os.getenv("POSTGRES_DB", "green_logistics_db")
    user = os.getenv("POSTGRES_USER", "green_admin")
    password = os.getenv("POSTGRES_PASSWORD", "GreenLogistics123!")

    print(f"[DB Service] Connecting to PostgreSQL at {host}:{port}/{dbname}")

    return psycopg.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password,
        connect_timeout=3
    )