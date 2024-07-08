import sqlite3
from contextlib import closing
import os


# Embeddings Database connection utility
def get_embeddings_db_connection(embeddings_db_model):
    conn = sqlite3.connect(f"./embeddings/{embeddings_db_model}.db")
    conn.row_factory = sqlite3.Row
    setup_embeddings_database(conn)
    return conn


# Database setup
def setup_embeddings_database(conn):
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


def get_lists_db_connection(db_file="main"):
    if os.path.exists(f"./lists/{db_file}.db") == False:
        needs_setup = True
    else:
        needs_setup = False

    conn = sqlite3.connect(f"./lists/{db_file}.db")
    conn.row_factory = sqlite3.Row

    if needs_setup:
        setup_lists_database(conn)
    return conn


def setup_lists_database(conn):
    with closing(conn.cursor()) as cursor:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS lists (
                id INTEGER PRIMARY KEY,
                list_name TEXT, 
                source TEXT, 
                content TEXT,
                tags TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
        """
        )

        conn.commit()


class ListManager:
    def __init__(self, db_name="main"):
        self.conn = get_lists_db_connection(db_name)
        self.cursor = self.conn.cursor()

    def get_list_items(self, list_name):
        self.cursor.execute("SELECT * FROM lists WHERE list_name = ?", (list_name,))
        row = self.cursor.fetchone()
        if row:
            return dict(row)
        return None

    def add_list_item(self, list_name, source, content, tags, _unique=True):
        if _unique:
            self.cursor.execute(
                "SELECT * FROM lists WHERE list_name = ? AND source = ? AND content = ? AND tags = ?",
                (list_name, source, content, tags),
            )
            row = self.cursor.fetchone()
            if row:
                return
        self.cursor.execute(
            "INSERT INTO lists (list_name, source, content, tags) VALUES (?, ?, ?, ?)",
            (list_name, source, content, tags),
        )
        self.conn.commit()

    def delete_list(self, list_name):
        self.cursor.execute("DELETE FROM lists WHERE list_name = ?", (list_name,))
        self.conn.commit()

    def list_lists(self):
        self.cursor.execute("SELECT * FROM lists")
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]


# KVstore Database connection utility
def get_kv_store_db_connection(db_file="main"):
    if os.path.exists(f"./kv_stores/{db_file}.db") == False:
        needs_setup = True
    else:
        needs_setup = False

    conn = sqlite3.connect(f"./kv_stores/{db_file}.db")
    conn.row_factory = sqlite3.Row

    if needs_setup:
        setup_kv_store_database(conn)
    return conn


def setup_kv_store_database(conn):
    with closing(conn.cursor()) as cursor:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS kvstore (
                id INTEGER PRIMARY KEY,
                key TEXT, 
                value TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
        """
        )

        conn.commit()


class KV_Store:
    def __init__(self, db_name="main"):
        self.conn = get_kv_store_db_connection(db_name)
        self.cursor = self.conn.cursor()

    def get(self, key):
        self.cursor.execute("SELECT value FROM kvstore WHERE key = ?", (key,))
        row = self.cursor.fetchone()
        if row:
            return row["value"]
        return None

    def set(self, key, value):
        # insert or update
        self.cursor.execute("SELECT * FROM kvstore WHERE key = ?", (key,))
        row = self.cursor.fetchone()
        if row:
            self.cursor.execute(
                "UPDATE kvstore SET value = ? WHERE key = ?", (value, key)
            )
        else:
            self.cursor.execute(
                "INSERT INTO kvstore (key, value) VALUES (?, ?)", (key, value)
            )
        self.conn.commit()

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        return self.set(key, value)

    def delete(self, key):
        self.cursor.execute("DELETE FROM kvstore WHERE key = ?", (key,))
        self.conn.commit()

    def list(self):
        self.cursor.execute("SELECT * FROM kvstore")
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]
