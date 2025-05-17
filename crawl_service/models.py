from pydantic import BaseModel
from typing import List, Optional
from config import TARGET_POSTS

class CrawlRequest(BaseModel):
    url: str
    target_posts: Optional[int] = TARGET_POSTS

class CrawlResponse(BaseModel):
    url: str
    posts: List[str]
    message: str

class TextInput(BaseModel):
    content: str
    url: str | None = None

class ClassifiedInput(BaseModel):
    content: str
    url: str | None = None
    label: str
    probability: float
    probabilities: dict