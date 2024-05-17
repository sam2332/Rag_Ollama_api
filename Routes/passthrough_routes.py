import logging
from contextlib import closing
from numpy import array, fromstring, argsort
from sklearn.metrics.pairwise import cosine_similarity
from fastapi import HTTPException
from Libs.DB import get_db_connection
from Libs.Utility import digest_str_duration
from Libs.FolderBasedCache import FolderBasedCache
from Libs.RequestSchema import ChatPassthroughRequest, ChatPassthroughRagRequest
from Libs.Utility import hash_ChatPassthroughRequest

import requests

from Libs.CONSTANTS import base_system_message


def register_routes(app):
    pt_cache = FolderBasedCache("pt_cache")

    @app.post("/api/passthrough/chat")
    async def passthrough_chat(data: ChatPassthroughRequest):
        data_hash = hash_ChatPassthroughRequest(data)
        if pt_cache.get(data_hash):
            return pt_cache.get(data_hash)
        # Create the URL for the chat API endpoint
        url = f"{app.config.get('ollama_host')}/api/chat"
        logging.info(f"Recieved chat request to {url} with payload: {data.dict()}")
        # Prepare the payload with all possible fields
        payload = {
            "model": data.model,
            "messages": [
                {"role": msg.role, "content": msg.content} for msg in data.messages
            ],
            "format": "json",
            "options": {
                "temperature": data.temperature,
            },
            "stream": False,
            "max_tokens": data.max_tokens,
            "keep_alive": "1m",
        }
        logging.info(f"Sending chat request to {url} with payload: {payload}")
        # Send the request to the external chat API
        response = requests.post(url, json=payload)
        logging.info(
            f"Recieved {response.status_code} response from chat request: {response.text}"
        )
        # Check if the request was successful
        if response.status_code == 200:
            # Return the response from the external service
            res_data = response.json()
            while (
                res_data["message"]["content"].strip() != res_data["message"]["content"]
            ):
                res_data["message"]["content"] = res_data["message"]["content"].strip()
            pt_cache.set(data_hash, res_data, digest_str_duration(data.cache))
            logging.info(f"Recieved response from chat request: {res_data}")
            return res_data
        else:
            # Return an error if something went wrong
            raise HTTPException(
                status_code=response.status_code,
                detail="Error processing chat request with external model",
            )

    @app.post("/api/passthrough/rag_chat")
    async def rag_passthrough_chat(data: ChatPassthroughRagRequest):
        data_hash = hash_ChatPassthroughRequest(data)
        if pt_cache.get(data_hash):
            return pt_cache.get(data_hash)
        # Create a connection to the database
        with get_db_connection(data.embeddings_model_db) as conn:
            with closing(conn.cursor()) as cursor:
                # Retrieve all embeddings from the database
                cursor.execute(
                    "SELECT source, content, embedding FROM embeddings where "
                )
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
