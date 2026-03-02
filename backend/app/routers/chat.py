from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.chat.chat_service import get_system_prompt, chat_with_client
from app.chat.schemas import ChatMessage, ChatResponse

router = APIRouter()

@router.post("/chat")
def chat(message: ChatMessage, db: Session = Depends(get_db)):
    system_prompt = get_system_prompt(db)
    response = chat_with_client(message, system_prompt, db)
    return {"response": response}