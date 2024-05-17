import requests
from contextlib import closing
from fastapi import HTTPException
from Libs.DB import get_db_connection
from Libs.Utility import make_embeddings_safe_for_db


def make_embeddings_safe_for_db(embedding):
    return str(embedding).replace("[", "{").replace("]", "}")


def gather_embeddings(embeddings_db, prompt, related_count):
    with get_db_connection(embeddings_db) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute("SELECT content, embedding FROM embeddings")
            embeddings = cursor.fetchall()
            query_emb = generate_embedding(prompt)
            db_embs = [
                np.fromstring(row["embedding"][1:-1], sep=",") for row in embeddings
            ]
            cos_sims = cosine_similarity([query_emb], db_embs)[0]
            indices = np.argsort(cos_sims)[::-1][:related_count]
            return indices


def insert_embedding(embeddings_db, content, source, check_existing=True):
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


def generate_embedding(prompt):
    response = requests.post(
        app.config.get("ollama_host") + "/api/embeddings",
        json={"model": app.config.get("embeddings_model"), "prompt": prompt},
    )
    if response.status_code == 200:
        return response.json()["embedding"]
    else:
        raise Exception("Error generating embeddings")
