import os
from dotenv import load_dotenv
from openai import OpenAI
from app import models
from sqlalchemy.orm import Session
from app.chat.schemas import ChatMessage

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def get_system_prompt(db: Session) -> str:
    hairdressers = db.query(models.Hairdresser).filter(
        models.Hairdresser.is_active == True
    ).all()
    services = db.query(models.Service).all()

    hairdressers_list = ", ".join([hairdresser.first_name for hairdresser in hairdressers])
    services_list = ", ".join([service.name for service in services])

    return f"""Jesteś pomocnym asystentem salony fryzjerskiego Aleksander.
    Pomagasz klientom umawiać wizytę.
    Dostepni fryzjerzy: {hairdressers_list}.
    Dostępne usługi: {services_list}.
    Zbierz od klienta następujace dane:
    - imię i nazwisko
    - numer telefonu
    - wybranego fryzjera (użyj dokładnej nazy z listy)
    - wybraną usługę (użyj dokładnej nazwy z listy)
    - preferowaną datę i godzinę.
    """

def chat_with_client(message: ChatMessage, system_prompt: str) -> str:
    messages = [{"role": "system", "content": system_prompt}]
    messages += message.history
    messages.append({"role": "user", "content": message.message})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    return response.choices[0].message.content