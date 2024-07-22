from typing import List, Optional
from pydantic import BaseModel


class BatchEmbeddingRequest(BaseModel):
    embeddings: List[EmbeddingRequest]
