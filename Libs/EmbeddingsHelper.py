import requests
from contextlib import closing
from fastapi import HTTPException
from Libs.DB import get_db_connection

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def make_embeddings_safe_for_db(embedding):
    return str(embedding).replace("[", "{").replace("]", "}")


def gather_embeddings(app, embeddings_db, prompt, related_count):
    with get_db_connection(embeddings_db) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute("SELECT content,source, embedding FROM embeddings")
            embeddings = cursor.fetchall()
            if len(embeddings) == 0:
                return []
            query_emb = generate_embedding(app, prompt)
            db_embs = [
                np.fromstring(row["embedding"][1:-1], sep=",") for row in embeddings
            ]
            cos_sims = cosine_similarity([query_emb], db_embs)[0]
            indices = np.argsort(cos_sims)[::-1][:related_count]
            return [embeddings[i] for i in indices]


def insert_embedding(app, embeddings_db, content, source, check_existing=True):
    content = "".join(content).strip()
    print(
        f"Inserting into {embeddings_db} embedding for {len(content)} bytes from {source}"
    )
    response = requests.post(
        app.config.get("ollama_host") + "/api/embeddings",
        json={"model": app.config.get("embeddings_model"), "prompt": content},
    )
    if response.status_code == 200:
        embedding = response.json()["embedding"]
        with get_db_connection(embeddings_db) as conn:
            with closing(conn.cursor()) as cursor:
                embedding = make_embeddings_safe_for_db(embedding)
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
    else:
        raise HTTPException(
            status_code=response.status_code, detail="Error processing embeddings"
        )


def generate_embedding(app, prompt):
    response = requests.post(
        app.config.get("ollama_host") + "/api/embeddings",
        json={"model": app.config.get("embeddings_model"), "prompt": prompt},
    )
    if response.status_code == 200:
        return response.json()["embedding"]
    else:
        raise Exception("Error generating embeddings")


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
