from typing import List, Optional
from pydantic import BaseModel


class EmbeddingUrlRequest(BaseModel):
    url: str
    check_existing: bool
    embeddings_db: str
    chunk_size: int = 255
    overlap: int = 50
