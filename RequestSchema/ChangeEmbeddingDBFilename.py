from typing import List, Optional
from pydantic import BaseModel


class ChangeEmbeddingDBFilename(BaseModel):
    name: str
