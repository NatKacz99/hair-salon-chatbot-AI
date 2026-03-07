from pydantic import BaseModel
import string
from typing import Optional
from typing import List

class ChatMessage(BaseModel):
    message: str
    history: List[dict] = []

class ChatResponse(BaseModel):
    response: str

class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[int] = None