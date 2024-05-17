from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import requests
import time
import sqlite3
import json
from contextlib import closing
import numpy as np
import os
import logging

from Libs.ConfigFile import ConfigFile
from Libs.RequestSchema import (
    EmbeddingRequest,
    RagRequest,
    ChangeEmbeddingDBFilename,
    ChatPassthroughRequest,
)
from Libs.FolderBasedCache import FolderBasedCache
from Libs.Utility import digest_str_duration, hash_ChatPassthroughRequest
from Libs.DB import setup_database
from Libs.CONFIG import get_config

from Libs.ModelHelper import check_model_exists, list_available_models

config = get_config()

logging.basicConfig(level=logging.INFO)
app = FastAPI()
app.config = config


# add cors

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


# cache class where items expire after a certain seconds, there are get/set/save/restore/cleanup methods clean should be called on get  and save on set, use jsonpickle


from Routes.passthrough_routes import register_routes as register_passthrough_routes

register_passthrough_routes(app)


from Routes.embeddings_routes import register_routes as register_embeddings_routes

register_embeddings_routes(app)

from Routes.rag_routes import register_routes as register_rag_routes

register_rag_routes(app)

# serve index.html
from fastapi.responses import FileResponse


# import all files in the "ingress" folder and mark the filenames as the source use the pathlib
from pathlib import Path

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=11435)
