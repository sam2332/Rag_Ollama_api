import sqlite3
from contextlib import closing
import os
import pytest
from Libs.DB import setup_database, get_db_connection
import unittest
import random
from unittest.mock import patch


class TestDB(unittest.TestCase):
    def test_setup_database(self):
        fn = "testing" + "-".join(
            [random.choice(["a", "b", "c"]) for i in range(0, 10)]
        )
        with get_db_connection(fn) as conn:
            pass
        self.assertEqual(True, os.path.exists(f"./embeddings/{fn}.db"))
        os.remove(f"./embeddings/{fn}.db")

    def test_persistance(self):
        db1 = "test1" + "-".join([random.choice(["a", "b", "c"]) for i in range(0, 10)])
        db2 = "test2" + "-".join([random.choice(["a", "b", "c"]) for i in range(0, 10)])
        with get_db_connection(db1) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute(
                    "INSERT INTO embeddings (source, content, embedding) VALUES ('source1', 'content1', 'embedding1')"
                )
                conn.commit()
        os.rename(f"./embeddings/{db1}.db", f"./embeddings/{db2}.db")
        with get_db_connection(db2) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute("SELECT * FROM embeddings")
                rows = cursor.fetchall()
                assert len(rows) == 1
                assert rows[0]["source"] == "source1"
                assert rows[0]["content"] == "content1"
                assert rows[0]["embedding"] == "embedding1"
                conn.commit()
        os.remove(f"./embeddings/{db2}.db")
