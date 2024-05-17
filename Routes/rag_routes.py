from fastapi import HTTPException
from numpy import array, argsort, fromstring
from sklearn.metrics.pairwise import cosine_similarity
from pydantic import BaseModel


from Libs.RequestSchema import RagRequest
from Libs.CONSTANTS import base_system_message


def register_routes(app):
    # Retrieval-Augmented Generation using embeddings
    @app.post("/api/rag_test")
    async def perform_ragtest(data: RagRequest):
        with get_db_connection(data.embeddings_db) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute("SELECT content, embedding FROM embeddings")
                embeddings = cursor.fetchall()
                query_emb = generate_embedding(data.prompt)
                db_embs = [
                    np.fromstring(row["embedding"][1:-1], sep=",") for row in embeddings
                ]
                cos_sims = cosine_similarity([query_emb], db_embs)[0]
                indices = np.argsort(cos_sims)[::-1][:3]
                related_prompts = " ".join(embeddings[i]["content"] for i in indices)
                system_prompt = base_system_message + related_prompts

                return {
                    "system_prompt": system_prompt,
                    "related_prompts": related_prompts,
                }

    @app.post("/api/rag")
    async def perform_rag(data: RagRequest):
        # Create a connection to the database
        with get_db_connection(data.embeddings_db) as conn:
            with closing(conn.cursor()) as cursor:
                # Retrieve all embeddings from the database
                cursor.execute("SELECT source, content, embedding FROM embeddings")
                embeddings = cursor.fetchall()

                # Generate the embedding for the prompt
                query_emb = array([generate_embedding(data.prompt)])

                # Convert stored embeddings from strings back to numpy arrays

                db_embs = array(
                    [fromstring(emb["embedding"][1:-1], sep=",") for emb in embeddings]
                )

                # Compute cosine similarities
                cos_sims = cosine_similarity(query_emb, db_embs)[0]
                indices = argsort(cos_sims)[::-1][
                    : data.related_count
                ]  # Top 3 related prompts

                # Construct related prompts text
                related_prompts = ""
                # "\n".join(embeddings[i]['content'] for i in indices)
                for i in indices:
                    related_prompts += f"""
    #{embeddings[i]['source']}
    ```
    {embeddings[i]['content']}
    ```"""

                system_prompt = f"{base_system_message} \n{related_prompts}\nThe next message is the users question"
                print()

                print(system_prompt)
                print(data.prompt)
                # Query an external chat model
                response = requests.post(
                    app.config.get("ollama_host") + "/api/chat",
                    json={
                        "stream": False,
                        "model": app.config.get("chat_model"),
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": data.prompt},
                        ],
                        "max_tokens": data.max_tokens,
                    },
                )
                print(response.status_code)
                print(response.text)
                if response.status_code == 200:
                    print(response.json())
                    print()
                    return response.json()
                else:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail="Error processing chat with model",
                    )
