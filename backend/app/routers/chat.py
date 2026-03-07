from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.chat.chat_service import get_system_prompt, chat_with_client
from app.chat.schemas import ChatMessage, ChatResponse
from app.models import Conversation, Message

router = APIRouter()

@router.post("/chat")
def chat(message: ChatMessage, db: Session = Depends(get_db)):
    if message.conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.conversation_id == message.conversation_id
        ).first()
    else: 
        conversation = Conversation()
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    user_message = Message(
        conversation_id=conversation.conversation_id,
        role="user",
        content=message.message
    )
    db.add(user_message)
    db.commit()
    
    messages = db.query(Message).filter(
        Message.conversation_id == conversation.conversation_id
    ).order_by(Message.created_at).all()

    history_for_llm = [
        {"role": message.role, "content": message.content}
        for message in messages
    ]

    system_prompt = get_system_prompt(db)
    response = chat_with_client(
        message=message.message, 
        system_prompt=system_prompt, 
        history=history_for_llm,
        db=db
    )

    assistant_message = Message(
        conversation_id=conversation.conversation_id,
        role="assistant",
        content=response
    )

    db.add(assistant_message)
    db.commit()
    return {
        "response": response,
        "conversation_id": conversation.conversation_id
    }