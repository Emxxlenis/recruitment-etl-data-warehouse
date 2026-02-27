import pandas as pd
from sqlalchemy import text
import db

def truncate_table(table_name, conn):
    """Clear table before loading new data (idempotent behavior)."""
    conn.execute(text(f"DELETE FROM {table_name}"))

def load_data(data_dict):
    """
    Load DataFrames into the Data Warehouse.
    """
    engine = db.get_engine()
    
    # Load order to preserve referential integrity (dimensions first, fact last)
    load_order = [
        'dim_technology', 
        'dim_seniority', 
        'dim_country', 
        'dim_candidate', 
        'dim_date',
        'fact_applications'
    ]
    
    print("Starting Data Warehouse load...")
    
    with engine.begin() as conn:  # Open a transaction
        for table_name in load_order:
            if table_name in data_dict:
                df = data_dict[table_name]
                
                # 1. Clear existing data (full refresh strategy)
                # In a real incremental setup, this would be UPSERT/MERGE logic
                truncate_table(table_name, conn)
                
                # 2. Insert in batches for scalability
                # chunksize=1000 is a practical local default for SQLite/Postgres
                df.to_sql(
                    table_name, 
                    conn, 
                    if_exists='append', 
                    index=False, 
                    chunksize=1000
                )
                print(f"Loaded table: {table_name} ({len(df)} rows)")
            else:
                print(f"Warning: no data found for {table_name}")
                
    print("Load completed successfully.")