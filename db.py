import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL") 

def get_db_connection():
    conn = pyodbc.connect(DATABASE_URL)
    return conn
