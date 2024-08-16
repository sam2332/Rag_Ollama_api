import os
import requests
from contextlib import closing
from fastapi import HTTPException
from Libs.DB import get_embeddings_db_connection
from Libs.Utility import data_spy

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import Libs.Ollama as Ollama


def make_embeddings_safe_for_db(embedding):
    return str(embedding).replace("[", "{").replace("]", "}")


from contextlib import closing
from fastapi import HTTPException

from numpy import array, argsort, fromstring
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def gather_embeddings(app, embeddings_db, prompt, related_count):
    with get_embeddings_db_connection(embeddings_db) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute("SELECT content, source, embedding FROM embeddings")
            embeddings = cursor.fetchall()
            if len(embeddings) == 0:
                return []

            # Generate the embedding for the prompt
            query_emb = Ollama.get_embedding(prompt)
            app.logger.debug(query_emb)
            # Convert stored embeddings from strings back to numpy arrays
            db_embs = [np.fromstring(emb[2][1:-1], sep=",") for emb in embeddings]

            # Compute cosine similarities
            cos_sims = cosine_similarity([query_emb], db_embs)[0]
            indices = argsort(cos_sims)[::-1][
                :related_count
            ]  # Top 'related_count' related prompts
            return [embeddings[i] for i in indices]


def insert_embedding(app, embeddings_db, content, source, check_existing=True):
    content = "".join(content).strip()
    data_spy(content, "embeddings_spy")
    app.logger.info(
        f"Inserting into {embeddings_db} embedding for {len(content)} bytes from {source}"
    )
    with get_embeddings_db_connection(embeddings_db) as conn:
        with closing(conn.cursor()) as cursor:
            embedding = make_embeddings_safe_for_db(Ollama.get_embedding(content))
            if check_existing:
                cursor.execute(
                    "SELECT * FROM embeddings WHERE source = ? AND content = ?",
                    (source, content),
                )
                if cursor.fetchone():
                    return {
                        "status": "existing",
                        "content": content,
                        "embedding": embedding,
                    }
            cursor.execute(
                "INSERT INTO embeddings (source, content, embedding) VALUES (?, ?, ?)",
                (source, content, embedding),
            )
            conn.commit()
            return {"status": "success", "content": content, "embedding": embedding}


def compactText(text):
    lines = text.splitlines()
    lines = [line.rstrip() for line in lines]

    # delete stripped empty lines
    lines = [line for line in lines if line]

    text = "\n".join(lines)

    # compact multiple spaces into one
    old = text
    while True:
        text = text.replace("  ", " ")
        if old == text:
            break
        old = text
    return text


def SoupToText(soup):
    # cleanup the soup

    # kill all script and style elements
    for script in soup(
        [
            "script",
            "style",
            "head",
            "title",
            "meta",
            "[document]",
            "noscript",
            "svg",
            "button",
            "a",
            "img",
            "input",
            "select",
            "textarea",
            "option",
            "form",
            "label",
            "fieldset",
            "legend",
        ]
    ):
        script.extract()  # rip it out

    # get text
    text = compactText(soup.get_text())

    return text
