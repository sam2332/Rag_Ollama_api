import dotenv
import sys
from pathlib import Path

sys.path.insert(0, Path(".").absolute())
dotenv.load_dotenv()

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

from Libs.RequestSchema import (
    EmbeddingRequest,
    RagRequest,
    ChangeEmbeddingDBFilename,
    ChatPassthroughRequest,
)
from Libs.FolderBasedCache import FolderBasedCache
from Libs.DB import setup_embeddings_database

from Libs.ModelHelper import check_model_exists, list_available_models


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI()


# add cors

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

import importlib
import os

# cache class where items expire after a certain seconds, there are get/set/save/restore/cleanup methods clean should be called on get  and save on set, use jsonpickle
defined_functions = {}
for file in os.listdir("Routes"):
    if file.endswith(".py"):
        try:
            module_filename = file.replace(".py", "")
            logger.info(f"Importing module {module_filename}")
            module = importlib.import_module(f"Routes.{module_filename}")
            module.register_routes(app)

            defined_functions[module_filename] = module
            logger.info(f"Imported module {module_filename}")

        except Exception as e:
            logger.error(f"Error importing module {module_filename}: {e}")
            # traceback to logger
            import traceback

            logger.error(traceback.format_exc())


# serve index.html
from fastapi.responses import FileResponse


# import all files in the "ingress" folder and mark the filenames as the source use the pathlib
from pathlib import Path

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=11435)
