from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Depends
from fastapi import FastAPI

from pydantic import BaseModel


# Path: Routes/functional_routes.py
import os
import importlib


class FunctionalRequest(BaseModel):
    function: str
    args: dict


def register_routes(app):
    defined_functions = {}
    for file in os.listdir("functional_functions"):
        if file.endswith(".py"):
            module_filename = file.replace(".py", "")

            module = importlib.import_module(f"functional_functions.{module_filename}")
            module.define_function(app)

            defined_functions[module_filename] = module
