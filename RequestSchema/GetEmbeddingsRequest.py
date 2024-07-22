from typing import List, Optional
from pydantic import BaseModel


class GetEmbeddingsRequest(BaseModel):
    embeddings_db: str
