from typing import List, Optional
from pydantic import BaseModel

from RequestSchema.Message import Message


class ChatPassthroughRequest(BaseModel):
    model: str
    messages: List[Message]
    cache: str
    max_tokens: int
    temperature: Optional[float] = 0.0
    top_p: Optional[float] = 1.0
    return_json: Optional[bool] = False
