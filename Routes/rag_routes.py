from fastapi import HTTPException
from numpy import array, argsort, fromstring
from sklearn.metrics.pairwise import cosine_similarity
from pydantic import BaseModel
from Libs.Embeddings_helper import generate_embedding

from Libs.RequestSchema import RagRequest
from Libs.CONSTANTS import base_system_message


def register_routes(app):
    # Retrieval-Augmented Generation using embeddings
    @app.post("/api/rag_test")
    async def perform_ragtest(data: RagRequest):
        related = gather_embeddings(data.embeddings_db, data.prompt, 3)
        related_prompts = ""
        for i in related:
            related_prompts += f"""
#{embeddings[i]['source']}
```
{embeddings[i]['content']}
```"""
        system_prompt = f"{base_system_message} \n{related_prompts}"
        return {"system_prompt": system_prompt, "related_prompts": related_prompts}

    @app.post("/api/rag")
    async def perform_rag(data: RagRequest):
        # Create a connection to the database
        related = gather_embeddings(data.embeddings_db, data.prompt, 3)
        related_prompts = ""
        for i in related:
            related_prompts += f"""
#{embeddings[i]['source']}
```
{embeddings[i]['content']}
```"""
        system_prompt = f"{base_system_message} \n{related_prompts}"
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
