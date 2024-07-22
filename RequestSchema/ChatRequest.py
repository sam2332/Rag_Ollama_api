from typing import List, Optional
from pydantic import BaseModel


class ChatRequest(BaseModel):
    messages: list
