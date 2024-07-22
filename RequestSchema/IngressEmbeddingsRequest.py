from typing import List, Optional
from pydantic import BaseModel


class IngressEmbeddingsRequest(BaseModel):
    overlap: int = 50
    chunk_size: int = 255
    embeddings_db: str
