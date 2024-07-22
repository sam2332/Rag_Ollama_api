from typing import List, Optional
from pydantic import BaseModel


class IngressFastCSVEmbeddingsRequest(BaseModel):
    embeddings_db: str
    lines_chunking_size: int = 5
    ignore_first_line: bool = True
    thread_count: int = 10
