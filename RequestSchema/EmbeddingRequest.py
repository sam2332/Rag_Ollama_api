from typing import List, Optional
from pydantic import BaseModel


class EmbeddingRequest(BaseModel):
    source: str
    content: str
    overlap: int = 50
    chunk_size: int = 255
    check_existing: bool = True
    embeddings_db: str
