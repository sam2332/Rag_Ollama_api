from typing import List, Optional
from pydantic import BaseModel

from RequestSchema.Message import Message


class ChatPassthroughRagRequest(BaseModel):
    model: str
    messages: List[Message]
    cache: str
    max_tokens: int
    temperature: Optional[float] = 0.0
    related_count: int
    embeddings_db: str
