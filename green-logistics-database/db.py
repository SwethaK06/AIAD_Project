#file is used to connect to the PostgreSQL database via the libraries and environment variables defined in the .env file 
import os
from pathlib import Path
import psycopg
from dotenv import load_dotenv

# Load central root .env file if present (do not override container env vars) - indiciating where to look for the .env file 
root_env = Path(__file__).resolve().parent.parent / ".env" #looks 2 folders levels up from current file 
local_env = Path(__file__).resolve().parent / ".env" #looks in the same folder as current file 

if root_env.exists(): #if the root .env file exists, load its environment variables
    load_dotenv(dotenv_path=root_env, override=False)
elif local_env.exists(): #if the root .env does not exist, check for a local .env file instead
    load_dotenv(dotenv_path=local_env, override=False)# override=False ensures that existing environment variables are not overwritten by the .env file

#used in app.py to make connection to PostgreSQL database via the environmental variables 
def get_db_connection():
    #connection details that are retrieved from the .env file
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    dbname = os.getenv("POSTGRES_DB")
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")

    print(f"[DB Service] Connecting to PostgreSQL at {host}:{port}/{dbname}")
    #actually creates the connection to the database 
    return psycopg.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password,
        connect_timeout=5 #if connection cannot be established within 5 seconds, it will timeout and throw an error
    )