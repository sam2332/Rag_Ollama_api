from typing import List, Optional, Dict, Any  # Import Any from typing module
from pydantic import BaseModel


# API models
class EmbeddingRequest(BaseModel):
    source: str
    content: str
    overlap: int = 50
    chunk_size: int = 255
    check_existing: bool = True
    embeddings_db: str


class ResetEmbeddingsRequest(BaseModel):
    embeddings_db: str


class GetEmbeddingsRequest(BaseModel):
    embeddings_db: str


class ChatRequest(BaseModel):
    messages: list


class BatchEmbeddingRequest(BaseModel):
    embeddings: List[EmbeddingRequest]


class RagRequest(BaseModel):
    prompt: str
    # optional system_message
    system_message: Optional[str] = None
    model: str
    related_count: int = 15
    max_tokens: int = 100
    embeddings_db: str
    temperature: Optional[float] = 0.9


class ChangeEmbeddingDBFilename(BaseModel):
    name: str


class ChangeEmbeddingModel(BaseModel):
    name: str


class Message(BaseModel):
    role: str  # 'system', 'user', or 'assistant'
    content: str


class ChatPassthroughRequest(BaseModel):
    model: str
    messages: List[Message]
    cache: str
    max_tokens: int
    temperature: Optional[float] = 0.0
    return_json: Optional[bool] = False


class ChatPassthroughRagRequest(BaseModel):
    model: str
    messages: List[Message]
    cache: str
    max_tokens: int
    temperature: Optional[float] = 0.0
    related_count: int
    embeddings_db: str


class GetEmbeddingsRequest(BaseModel):
    embeddings_db: str


class IngressEmbeddingsRequest(BaseModel):
    overlap: int = 50
    chunk_size: int = 255
    embeddings_db: str


class IngressFastCSVEmbeddingsRequest(BaseModel):
    embeddings_db: str
    lines_chunking_size: int = 5
    ignore_first_line: bool = True
    thread_count: int = 10


class EmbeddingUrlRequest(BaseModel):
    url: str
    check_existing: bool
    embeddings_db: str
    chunk_size: int = 255
    overlap: int = 50
