#this file is used to import the get_db_connection function from db.py and make it available for use in other modules that use db_pr.py 
from db import get_db_connection

__all__ = ["get_db_connection"]