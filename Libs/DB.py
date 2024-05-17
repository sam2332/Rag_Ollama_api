import sqlite3
from contextlib import closing
import os



# Database connection utility
def get_db_connection(embeddings_db_model):
    needs_setup = False
    if not os.path.exists(f"./embeddings/{embeddings_db_model}.db"):
        needs_setup = True
    conn = sqlite3.connect(f"./embeddings/{embeddings_db_model}.db")
    conn.row_factory = sqlite3.Row
    if needs_setup:
        setup_database(embeddings_db_model)
    return conn


# Database setup
def setup_database(embeddings_model_db):
    with get_db_connection(config) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS embeddings (
                    id INTEGER PRIMARY KEY,
                    source TEXT, 
                    content TEXT, 
                    embedding TEXT
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
            """)

            conn.commit()
