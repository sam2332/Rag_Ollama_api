import sqlite3
from contextlib import closing
import os


# Database connection utility
def get_db_connection(embeddings_db_model):
    conn = sqlite3.connect(f"./embeddings/{embeddings_db_model}.db")
    conn.row_factory = sqlite3.Row
    setup_database(conn)
    return conn


# Database setup
def setup_database(conn):
    with closing(conn.cursor()) as cursor:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS embeddings (
                id INTEGER PRIMARY KEY,
                source TEXT, 
                content TEXT, 
                embedding TEXT
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
        """
        )

        conn.commit()
