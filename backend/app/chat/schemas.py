from pydantic import BaseModel
import string
from typing import Optional
from typing import List

class ChatBookingRequest(BaseModel):
    hairdresser_name: Optional[str]
    service_name: Optional[str]
    date: str
    time: str
    client_name: str
    client_phone: str
    notes: Optional[str] = None

class ChatMessage(BaseModel):
    message: str
    history: List[dict] = []

class ChatResponse(BaseModel):
    response: str