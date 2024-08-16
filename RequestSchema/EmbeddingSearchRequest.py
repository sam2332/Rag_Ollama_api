from pydantic import BaseModel
from typing import List, Optional


class EmbeddingSearchRequest(BaseModel):
    embeddings_db: str
    query: Optional[str] = None
    queries: Optional[List[str]] = None
    max_related: int
    minimal_similarity: float
