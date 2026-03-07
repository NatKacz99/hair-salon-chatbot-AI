import os
from dotenv import load_dotenv
from openai import OpenAI
from app import models
from sqlalchemy.orm import Session
from app.chat.schemas import ChatMessage
import json
from app.chat.booking_service import create_booking_from_chat, check_availability_from_chat, cancel_booking_from_chat
from datetime import date

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

    today = date.today().strftime('%d.%m.%Y')

    return f"""Jesteś kuluralnym i pomocnym asystentem salonu fryzjerskiego Aleksander.
    Pomagasz klientom umawiać wizytę.
    Dostepni fryzjerzy: {hairdressers_list}.
    Dostępne usługi: {services_list}.
    Zbierz od klienta następujace dane:
    - imię i nazwisko
    - numer telefonu
    - wybranego fryzjera (użyj dokładnej nazwy z listy)
    - wybraną usługę (użyj dokładnej nazwy z listy)
    - preferowaną datę i godzinę.
    Dzisiaj jest {today}. Rezerwacje przyjmujemy od dziś wzwyż.
    Jeśli klient poda wszystkie dane potrzebne do rezerwacji:
    - imię i nazwisko
    - numer telefonu
    - fryzjera (może podać, ale nie musi)
    - usługę
    - datę i godzinę
    - uwagi do rezerwacji (może podać, ale nie musi) 
    nie zadawaj dodatkowych pytań i nie proś o potwierdzenie.
    Od razu wywołaj funkcję create_booking.
    Nie informuj klienta, że coś sprawdzisz później ani że ma czekać.
    System wykonuje operacje natychmiast i odpowiedź zawsze zawiera wynik.
    Jeśli brakuje jakiejś informacji potrzebnej do rezerwacji,
    poproś klienta tylko o brakującą informację.
    Jeśli wszystkie dane są podane w jednej wiadomości,
    natychmiast wykonaj rezerwację używając funkcji create_booking.
    """

tools  = [
    {
        "type": "function",
        "function": {
            "name": "create_booking",
            "description": "Tworzy rezereację wizyty do barbera, gdy klient poda wszystkie wymagane dane.",
            "parameters": {
                "type": "object",
                "properties": {
                    "client_name": {"type": "string", "description": "Imię oraz nazwisko klienta"},
                    "client_phone": {"type": "string", "description": "Numer telefonu klienta"},
                    "hairdresser_name": {"type": "string", "description": "Imię fryzjera, jeśli klient wskazał konkretnego. Jeśli klient nie podał fryzjera, pole może zostać pominięte i system automatycznie wybierze pierwszego dostęnego fryzjera."},
                    "service_name": {"type": "string", "description": "Nazwa usługi"},
                    "booking_datetime": {"type": "string", "description": "Data + godzina w formacie ISO 8601: YYYY-MM-DDTHH:MM:00, np. 2026-03-05T13:00:00"},
                    "notes": {
                        "type": "string",
                        "description": "Dodatkowe uwagi klienta co do rezerwacji, np. uwagi dotyczące strzyżenia"
                    }
                },
                "required": ["client_name", "client_phone", "service_name", "booking_datetime"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": "Sprawdza dostępne terminy dla danego fryzjera i daty",
            "parameters": {
                "type": "object",
                "properties": {
                    "hairdresser_name": {"type": "string", "description": "Imię fryzjera"},
                    "date": {"type": "string", "description": "Data w formacie: YYYY-MM-DD"},
                    "service_name": {"type": "string", "description": "Nazwa usługi"}
                },
                "required": ["hairdresser_name", "date", "service_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_booking",
            "description": "Anulowanie rezerwacji klienta",
            "parameters": {
                "type": "object",
                "properties": {
                    "client_phone": {"type": "string", "description": "Numer telefonu klienta"},
                    "booking_datetime": {"type": "string", "description": "Data i godzina rezerwacji w formacie ISO 8601: YYYY-MM-DDTHH:MM:00, np. 2026-03-05T13:00:00"}
                },
                "required": ["client_phone", "booking_datetime"]
            }
        }
    }
]

def chat_with_client(message: ChatMessage, system_prompt: str, history, db: Session) -> str:
    messages = [
        {"role": "system", "content": system_prompt},
        *history 
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    response_message = response.choices[0].message

    if response_message.tool_calls:
        tool_call = response_message.tool_calls[0]
        args = json.loads(tool_call.function.arguments)
        print("Arguments from GPT:", args)
        tool_name = tool_call.function.name
        print(f"Tool name: {tool_name}")

        if tool_name == "create_booking":
            result = create_booking_from_chat(args, db)
            print("Result from create_booking_from_chat:", result)
        elif tool_name == "check_availability":
            result = check_availability_from_chat(args, db)
        elif tool_name == "cancel_booking":
            result = cancel_booking_from_chat(args, db)
        else:
            result = {"status": "error", "message": "Nieznana operacja"}

        messages.append(response_message)

        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result)
        })
        print("Messages after tool call:", messages)

        second_response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tools,
            tool_choice="none"
        )

        answer = second_response.choices[0].message.content
        if not answer:
            answer = "Rezerwacja została zapisana. Czy mogę w czymś jeszcze pomóc?"
        return answer

    return response_message.content