import os
import logging
import requests
from fastapi import HTTPException

logging.basicConfig(level=logging.INFO)
from Libs.Utility import digest_str_duration, hash_anything
from Libs.FolderBasedCache import FolderBasedCache


pt_cache = FolderBasedCache("pt_cache")


def chat_query(messages, model, cache, max_tokens, temperature, top_p, return_json):
    data_hash = hash_anything(
        {
            "messages": messages,
            "model": model,
            "cache": cache,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "return_json": return_json,
        }
    )
    if pt_cache.get(data_hash):
        return pt_cache.get(data_hash)
    # Create the URL for the chat API endpoint
    url = f"{os.environ.get('ollama_host')}/api/chat"
    # Prepare the payload with all possible fields
    payload = {
        "model": model,
        "messages": messages,
        "options": {"temperature": temperature, "top_p": top_p},
        "stream": False,
        "max_tokens": max_tokens,
        "keep_alive": "1m",
    }
    if return_json:
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
        while res_data["message"]["content"].strip() != res_data["message"]["content"]:
            res_data["message"]["content"] = res_data["message"]["content"].strip()

        pt_cache.set(data_hash, res_data, digest_str_duration(cache))
        logging.info(f"Recieved response from chat request: {res_data}")
        return res_data
    else:
        # Return an error if something went wrong
        raise HTTPException(
            status_code=response.status_code,
            detail="Error processing chat request with external model",
        )


def get_embedding(content):
    response = requests.post(
        os.environ.get("ollama_host") + "/api/embeddings",
        json={"model": os.environ.get("embeddings_model"), "prompt": content},
    )
    if response.status_code == 200:
        embedding = response.json()["embedding"]
        return embedding
    else:
        raise HTTPException(
            status_code=response.status_code, detail="Error processing embeddings"
        )
