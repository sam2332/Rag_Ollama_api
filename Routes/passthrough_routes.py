import logging
from contextlib import closing
from numpy import array, fromstring, argsort
from sklearn.metrics.pairwise import cosine_similarity
from fastapi import HTTPException
from Libs.DB import get_embeddings_db_connection
from Libs.Utility import digest_str_duration, data_spy
from Libs.FolderBasedCache import FolderBasedCache
from RequestSchema.ChatPassthroughRequest import ChatPassthroughRequest
from RequestSchema.ChatPassthroughRagRequest import ChatPassthroughRagRequest

import requests

from Libs.CONSTANTS import base_system_message
import Libs.Ollama as Ollama


def register_routes(app):
    @app.post("/api/passthrough/chat", tags=["chat"])
    async def passthrough_chat(data: ChatPassthroughRequest):
        messages = [{"role": msg.role, "content": msg.content} for msg in data.messages]
        return_json = data.return_json
        model = data.model
        cache = data.cache
        max_tokens = data.max_tokens
        temperature = data.temperature
        top_p = data.top_p

        response = Ollama.chat_query(
            messages, model, cache, max_tokens, temperature, top_p, return_json
        )
        data_spy(
            {
                "messages": messages,
                "model": model,
                "cache": cache,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "response": response,
            },
            "pt_spy",
        )
        return response
