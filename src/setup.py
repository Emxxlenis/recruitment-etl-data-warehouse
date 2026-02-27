from sqlalchemy import text
import db
import config

def init_db():
    print("Initializing Data Warehouse schema...")
    engine = db.get_engine()
    
    # Read SQL schema file
    try:
        with open(config.SQL_SCRIPT_PATH, 'r') as file:
            sql_script = file.read()
            
        with engine.connect() as conn:
            # SQLite may not execute multiple statements in one call,
            # so we split by ';'
            statements = sql_script.split(';')
            for statement in statements:
                if statement.strip():
                    conn.execute(text(statement))
            
        print("Tables created successfully.")
    except FileNotFoundError:
        print(f"Error: SQL file not found at {config.SQL_SCRIPT_PATH}")
    except Exception as e:
        print(f"Error creating database schema: {e}")

if __name__ == "__main__":
    init_db()