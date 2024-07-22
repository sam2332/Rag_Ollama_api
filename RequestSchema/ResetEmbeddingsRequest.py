from typing import List, Optional
from pydantic import BaseModel


class ResetEmbeddingsRequest(BaseModel):
    embeddings_db: str
