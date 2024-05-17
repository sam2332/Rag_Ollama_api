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
            "options": {
                "temperature": data.temperature,
            },
            "stream": False,
            "max_tokens": data.max_tokens,
            "keep_alive": "1m",
        }
        if data.return_json:
            payload["format"] = "json"
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
