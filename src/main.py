import sys
import os

# Ensure Python can resolve local src modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from extract import extract_data
from transform import transform_data
from load import load_data
import config
import setup  # Optional: initial schema bootstrap


def main():
    print("=== ETL WORKSHOP PIPELINE ===")
    
    # Step 0: health check (optional but recommended)
    if not os.path.exists(config.DB_PATH):
        print("Warning: database not found. Running initial setup...")
        setup.init_db()

    # Step 1: Extract
    try:
        df_raw = extract_data(config.RAW_DATA_PATH)
    except Exception as e:
        print(f"Error: extract phase failed: {e}")
        return

    # Step 2: Transform
    # transform.py must return a dict keyed by exact SQL table names
    try:
        data_tables = transform_data(df_raw)
    except Exception as e:
        print(f"Error: transform phase failed: {e}")
        return

    # Step 3: Load
    try:
        load_data(data_tables)
    except Exception as e:
        print(f"Error: load phase failed: {e}")
        return
        
    print("Pipeline finished successfully.")

if __name__ == '__main__':
    main()