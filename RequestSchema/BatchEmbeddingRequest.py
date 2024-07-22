from typing import List, Optional
from pydantic import BaseModel

from RequestSchema.EmbeddingRequest import EmbeddingRequest


class BatchEmbeddingRequest(BaseModel):
    embeddings: List[EmbeddingRequest]
