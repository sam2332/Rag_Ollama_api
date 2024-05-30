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
import Libs.Ollama as Ollama


def register_routes(app):
    @app.post("/api/passthrough/chat")
    async def passthrough_chat(data: ChatPassthroughRequest):
        messages = [{"role": msg.role, "content": msg.content} for msg in data.messages]
        return_json = data.return_json
        model = data.model
        cache = data.cache
        max_tokens = data.max_tokens
        temperature = data.temperature
        return Ollama.chat_query(
            messages, model, cache, max_tokens, temperature, return_json
        )
