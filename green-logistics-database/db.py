import os
from pathlib import Path
import psycopg
from dotenv import load_dotenv

# Load central root .env file if present (do not override container env vars)
root_env = Path(__file__).resolve().parent.parent / ".env"
local_env = Path(__file__).resolve().parent / ".env"

if root_env.exists():
    load_dotenv(dotenv_path=root_env, override=False)
elif local_env.exists():
    load_dotenv(dotenv_path=local_env, override=False)

def get_db_connection():
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    dbname = os.getenv("POSTGRES_DB")
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")

    print(f"[DB Service] Connecting to PostgreSQL at {host}:{port}/{dbname}")

    return psycopg.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password,
        connect_timeout=5
    )