from typing import List, Optional
from pydantic import BaseModel


class RagRequest(BaseModel):
    prompt: str
    system_message: Optional[str] = None
    model: str
    related_count: int = 15
    max_tokens: int = 100
    embeddings_db: str
    temperature: Optional[float] = 0.9
