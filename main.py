import sys
import os
import logging
import re
import dotenv

dotenv.load_dotenv("default.env")
dotenv.load_dotenv(".env")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
if os.getenv("DEBUG", "False").lower() == "true":
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)


def handle_exception(exc_type, exc_value, exc_traceback):
    """This function logs unhandled exceptions."""
    if issubclass(exc_type, KeyboardInterrupt):
        # Handle KeyboardInterrupt differently to exit without an error message
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.error("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception

# Initialize the logger

# Get all the existing log files
existing_logs = [f for f in os.listdir(".") if re.match(r"^app.log(\.\d+)?$", f)]

# Sort the files by the index numbers
existing_logs.sort(key=lambda f: int(f.split(".")[-1]) if f != "app.log" else 0)

# Rename the current log file to the next available index
if os.path.exists("app.log"):
    if existing_logs:
        last_index = (
            int(existing_logs[-1].split(".")[-1]) if "." in existing_logs[-1] else 0
        )
    else:
        last_index = 0
    new_index = last_index + 1
    os.rename("app.log", f"app.log.{new_index}")
    existing_logs.append(f"app.log.{new_index}")

# Keep only the last 10 logs, delete the rest
if len(existing_logs) > 10:
    for log_file in existing_logs[:-10]:
        if os.path.exists(log_file):
            os.remove(log_file)


file_handler = logging.FileHandler("app.log")
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(file_handler)

logger.info("Logging setup is complete.")


import sys
from pathlib import Path

sys.path.insert(0, Path(".").absolute())

import os


# patch for langchain on linux
platform = sys.platform
if platform == "linux" or platform == "linux2":
    import pathlib

    temp = pathlib.PosixPath
    pathlib.PosixPath.startswith = lambda self, x: self.as_posix().startswith(x)
    pathlib.PosixPath.rstrip = lambda self, x: self.as_posix().rstrip(x)
    pathlib.PosixPath.lstrip = lambda self, x: self.as_posix().lstrip(x)

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import requests
import time
import sqlite3
import json
from contextlib import closing
import numpy as np

import os
import re

from RequestSchema.EmbeddingRequest import EmbeddingRequest
from RequestSchema.RagRequest import RagRequest
from RequestSchema.ChangeEmbeddingDBFilename import ChangeEmbeddingDBFilename
from RequestSchema.ChatPassthroughRequest import ChatPassthroughRequest

from Libs.FolderBasedCache import FolderBasedCache
from Libs.DB import setup_embeddings_database

from Libs.ModelHelper import check_model_exists, list_available_models

import os

# system exceptions
app = FastAPI()
app.logger = logger

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
            # logger.info(f"Importing module {module_filename}")
            module = importlib.import_module(f"Routes.{module_filename}")
            module.register_routes(app)

            defined_functions[module_filename] = module
            app.logger.info(f"Imported module {module_filename}")

        except Exception as e:
            logger.error(f"Error importing module {module_filename}: {e}")
            # traceback to logger
            import traceback

            app.logger.error(traceback.format_exc())


# serve index.html
from fastapi.responses import FileResponse


# import all files in the "ingress" folder and mark the filenames as the source use the pathlib
from pathlib import Path

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=11435)
