from contextlib import closing
from fastapi import HTTPException
from Libs.DB import get_embeddings_db_connection
import threading as threadding
from queue import Queue
import requests
import time
from pathlib import Path
import logging
from bs4 import BeautifulSoup
import os
from RequestSchema.BatchEmbeddingRequest import BatchEmbeddingRequest
from RequestSchema.ChangeEmbeddingDBFilename import ChangeEmbeddingDBFilename
from RequestSchema.ChangeEmbeddingModel import ChangeEmbeddingModel
from RequestSchema.ChatPassthroughRagRequest import ChatPassthroughRagRequest
from RequestSchema.ChatPassthroughRequest import ChatPassthroughRequest
from RequestSchema.ChatRequest import ChatRequest
from RequestSchema.EmbeddingRequest import EmbeddingRequest
from RequestSchema.EmbeddingUrlRequest import EmbeddingUrlRequest
from RequestSchema.GetEmbeddingsRequest import GetEmbeddingsRequest
from RequestSchema.IngressEmbeddingsRequest import IngressEmbeddingsRequest
from RequestSchema.IngressFastCSVEmbeddingsRequest import (
    IngressFastCSVEmbeddingsRequest,
)
from RequestSchema.Message import Message
from RequestSchema.RagRequest import RagRequest
from RequestSchema.ResetEmbeddingsRequest import ResetEmbeddingsRequest

from Libs.EmbeddingsHelper import (
    insert_embedding,
    make_embeddings_safe_for_db,
    SoupToText,
)

logging.basicConfig(level=logging.DEBUG)


def register_routes(app):
    @app.post("/api/embeddings/reset_embeddings_db", tags=["embeddings"])
    async def reset_embeddings_db(data: ResetEmbeddingsRequest):
        with get_embeddings_db_connection(data.embeddings_db) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute("DELETE FROM embeddings")
                conn.commit()
        os.unlink(os.path.join("embeddings", data.embeddings_db + ".db"))
        return {"status": "success"}

    # Endpoint to get all embeddings
    @app.get("/api/embeddings/", tags=["embeddings"])
    async def get_embeddings(data: GetEmbeddingsRequest):
        with get_embeddings_db_connection(data.embeddings_db) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute("SELECT * FROM embeddings")
                rows = cursor.fetchall()
                return [dict(row) for row in rows]

    def file_ingress_thread(file, embeddings_db):
        if file.suffix == ".txt":
            with open(file, "r") as f:
                content = f.read()
                # chunk content 255 characters
                for i in range(0, len(content), data.chunk_size):
                    insert_embedding(
                        app,
                        embeddings_db,
                        content[i : i + data.chunk_size],
                        file.name + " - chunk " + str(i),
                    )
        elif file.suffix == ".csv":
            file_data = file.read_text()
            lines = file_data.split("\n")
            avg_list = []
            for index in range(2, len(lines) - 1, 5):
                start = time.time()
                content = ""
                for i in range(data.overlap):
                    if index - i > 0:
                        content += lines[index - i] + "\n"
                content += lines[index] + "\n"

                for i in range(data.overlap):
                    if index + i < len(lines):
                        content += lines[index + i] + "\n"
                # add headers at top of content
                content = " ".join(lines[0:2]) + "\n" + content
                insert_embedding(
                    app, embeddings_db, content, file.name + " - line " + str(index)
                )
                end = time.time()
                avg_list.append(end - start)
                avg = sum(avg_list) / len(avg_list)
                print(
                    f"Average time: {avg} seconds, time remaining for {len(lines)-index} lines: {avg*(len(lines)-index)} seconds"
                )
                avg_list = avg_list[-10:]

    @app.post("/api/embeddings/ingress_file_embeddings/", tags=["embeddings"])
    async def ingress_file_embeddings(data: IngressEmbeddingsRequest):
        # Get all files in the ingress folder
        ingress_folder = Path("ingress")
        threads = []
        for file in ingress_folder.iterdir():
            if file.is_file():
                t = threadding.Thread(
                    target=file_ingress_thread,
                    args=(
                        file,
                        data.embeddings_db,
                    ),
                ).start()
                threads.append(t)
        for t in threads:
            t.join()
        return {"status": "success"}

    def ingress_thread(queue, embeddings_db):
        failout = 5
        while failout > 0:
            while not queue.empty():
                file, lines = queue.get()
                content = "\n".join(lines)
                try:
                    insert_embedding(app, embeddings_db, content, file)
                except Exception as e:
                    print(e)
                    failout -= 1
            failout - 1

    @app.post("/api/embeddings/fast_csv_ingress/", tags=["embeddings"])
    async def fast_csv_ingress(data: IngressFastCSVEmbeddingsRequest):
        queue = Queue()
        for file in Path("ingress").glob("*.csv"):
            lines = file.read_text().split("\n")
            for _ in range(data.thread_count):
                threadding.Thread(
                    target=ingress_thread,
                    args=(
                        queue,
                        data.embeddings_db,
                    ),
                ).start()

            start = 1
            if data.ignore_first_line:
                start = 2
            for index in range(start, len(lines) - 1, data.chunk_size):
                queue.put(
                    (
                        f"{file.name} - lines {index-2} - {index+2}",
                        lines[index - 2 : index + 3],
                    )
                )

        while queue.qsize() > 0:
            time.sleep(1)
        return {"status": "success"}

    # Endpoint to insert text and embeddings
    @app.post("/api/embeddings/insert_text_embeddings/", tags=["embeddings"])
    async def insert_text_embeddings(data: EmbeddingRequest):
        # Simulating external API call for embeddings
        chunk_size = data.chunk_size
        overlap = data.overlap
        content = data.content
        if len(content) < data.chunk_size:
            insert_embedding(
                app,
                embedding.embeddings_db,
                content,
                embedding.source,
                embedding.check_existing,
            )
        else:
            for i in range(0, len(content), chunk_size - overlap):
                chunk = content[i : i + chunk_size]
                insert_embedding(
                    app,
                    data.embeddings_db,
                    chunk,
                    data.source,
                    data.check_existing,
                )

    # Endpoint to insert text and embeddings
    @app.post("/api/embeddings/batch_insert_text_embeddings/", tags=["embeddings"])
    async def insert_text_embeddings_list(data: BatchEmbeddingRequest):
        for embedding in data.embeddings:
            chunk_size = embedding.chunk_size
            overlap = embedding.overlap
            content = embedding.content
            if len(content) < chunk_size:
                insert_embedding(
                    app,
                    embedding.embeddings_db,
                    content,
                    embedding.source,
                    embedding.check_existing,
                )
            else:
                for i in range(0, len(content), chunk_size - overlap):
                    chunk = content[i : i + chunk_size]
                    insert_embedding(
                        app,
                        embedding.embeddings_db,
                        chunk,
                        embedding.source,
                        embedding.check_existing,
                    )
