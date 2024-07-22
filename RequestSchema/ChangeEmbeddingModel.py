from typing import List, Optional
from pydantic import BaseModel


class ChangeEmbeddingModel(BaseModel):
    name: str
