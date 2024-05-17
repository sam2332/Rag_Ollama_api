
from typing import List, Optional, Dict, Any  # Import Any from typing module
from pydantic import BaseModel


# API models
class EmbeddingRequest(BaseModel):
    db: str
    source: str
    content: str
    overlap: int = 50
    chunk_size: int = 255



class ChatRequest(BaseModel):
    messages: list

class RagRequest(BaseModel):
    prompt: str
    related_count: int
    max_tokens: int
    embeddings_db: str



class ChangeEmbeddingModel(BaseModel):
    name: str

class Message(BaseModel):
    role: str  # 'system', 'user', or 'assistant'
    content: str

class ChatPassthroughRequest(BaseModel):
    model: str
    messages: List[Message]
    cache :str
    max_tokens: int
    temperature: Optional[float] = 0.0

class ChatPassthroughRagRequest(BaseModel):
    model: str
    messages: List[Message]
    cache :str
    max_tokens: int
    temperature: Optional[float] = 0.0
    related_count: int
    embeddings_db: str


class IngressEmbeddingsRequest(BaseModel):
    overlap: int = 50
    chunk_size: int = 255

