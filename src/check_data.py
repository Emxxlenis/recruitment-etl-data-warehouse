import sqlite3
import pandas as pd
import os

# Connect
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "sql", "etl_workshop.db")
conn = sqlite3.connect(DB_PATH)

# 1. Validate record count (expected: 50k)
print("Total Applications:", pd.read_sql("SELECT COUNT(*) FROM fact_applications", conn).iloc[0,0])

# 2. Validate candidate dedup count (expected: ~49k)
print("Total Candidates:", pd.read_sql("SELECT COUNT(*) FROM dim_candidate", conn).iloc[0,0])

# 3. Display a hired sample
print("\nHired Sample:")
print(pd.read_sql("""
    SELECT t.technology_name, s.seniority_name, COUNT(*) as hired_count
    FROM fact_applications f
    JOIN dim_technology t ON f.technology_id = t.technology_id
    JOIN dim_seniority s ON f.seniority_id = s.seniority_id
    WHERE f.is_hired = 1
    GROUP BY t.technology_name, s.seniority_name
    LIMIT 5
""", conn))