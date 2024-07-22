import os
from fastapi import HTTPException
from numpy import array, argsort, fromstring
from sklearn.metrics.pairwise import cosine_similarity
from pydantic import BaseModel
from Libs.EmbeddingsHelper import gather_embeddings

from Libs.RequestSchema.RagRequest import RagRequest

from Libs.CONSTANTS import base_system_message

import requests


def register_routes(app):
    # Retrieval-Augmented Generation using embeddings
    @app.post("/api/rag_test", tags=["rag"])
    async def perform_ragtest(data: RagRequest):
        related = gather_embeddings(app, data.embeddings_db, data.prompt, 3)
        related_prompts = ""
        for i in related:
            related_prompts += f"""
#{i['source']}

{i['content']}

"""
        system_prompt = f"{base_system_message} \n{related_prompts}"
        return {"system_prompt": system_prompt, "related_prompts": related_prompts}

    @app.post("/api/rag", tags=["rag"])
    async def perform_rag(data: RagRequest):
        if data.system_message is not None:
            system_message = data.system_message
        else:
            system_message = base_system_message
        # Create a connection to the database

        related = gather_embeddings(
            app, data.embeddings_db, data.prompt, data.related_count
        )
        related_prompts = ""
        old_source = None
        for i in related:
            if i["source"] != old_source:
                related_prompts += f"\n# {i['source']}\n"
                old_source = i["source"]
            related_prompts += f"{i['content']}\n"

        system_prompt = f"{system_message} \n{related_prompts}"

        data_spy(
            {
                "system_prompt": system_prompt,
                "prompt": data.prompt,
                "model": data.model,
                "temperature": data.temperature,
                "max_tokens": data.max_tokens,
            },
            "rag_spy",
        )
        print(system_prompt)
        print(data.prompt)
        # Query an external chat model
        response = requests.post(
            os.environ.get("ollama_host") + "/api/chat",
            json={
                "stream": False,
                "model": data.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": data.prompt},
                ],
                "options": {"temperature": data.temperature},
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
