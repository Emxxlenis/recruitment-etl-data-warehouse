import os

# Project paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
SQL_DIR = os.path.join(BASE_DIR, 'sql')
RAW_DATA_PATH = os.path.join(DATA_DIR, 'raw', 'candidates.csv')
SQL_SCRIPT_PATH = os.path.join(SQL_DIR, 'create_tables.sql')

# Database configuration
# In production, use environment variables (os.getenv)
DB_NAME = 'hiring_analytics.db'
DB_PATH = os.path.join(SQL_DIR, DB_NAME)
DATABASE_URL = f"sqlite:///{DB_PATH}" 
# If scaling to Postgres: DATABASE_URL = "postgresql://user:pass@host:port/dbname"