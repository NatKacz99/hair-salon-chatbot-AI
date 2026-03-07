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

    return f"""Jesteś kulturalnym i pomocnym asystentem salonu fryzjerskiego Aleksander.
Pomagasz klientom umawiać wizytę.
Dostępni fryzjerzy: {hairdressers_list}.
Dostępne usługi: {services_list}.
Dzisiaj jest {today}. Rezerwacje przyjmujemy od dziś wzwyż.

Zasady obsługi rezerwacji:

1. Jeśli klient poda usługę, datę i godzinę wizyty:
   a) Najpierw sprawdź dostępność terminu używając funkcji check_availability.
   b) Jeśli termin jest **zajęty**, natychmiast poinformuj klienta, że termin jest 
      niedostępny i zaproponuj inną datę/godzinę podaną przez narzędzie. 
      Nie pytaj o dane klienta w tym przypadku.
   c) Jeśli termin jest **dostępny**:
      - Jeśli klient ma preferencje co do fryzjera:
          * Poproś o brakujące dane klienta (imię, nazwisko, numer telefonu), jeśli nie 
          są jeszcze dostępne.
          * Następnie wywołaj create_booking z polem hairdresser_name.
      - Jeśli klient nie ma preferencji co do fryzjera i masz już dane klienta:
          * Od razu wywołaj create_booking **bez pola hairdresser_name**.
      - Jeśli dane klienta są niekompletne, poproś tylko o brakujące informacje.

2. Jeśli klient wcześniej podał swoje dane (imię, nazwisko lub numer telefonu), użyj ich 
ponownie przy wywołaniu create_booking. Nie pytaj o nie ponownie, jeśli są dostępne 
w historii rozmowy.

3. Nigdy nie wywołuj create_booking bez wcześniejszego sprawdzenia dostępności (chyba że 
klient nie ma preferencji co do fryzjera i wszystkie dane są kompletne, wtedy system sam 
przypisze wolnego fryzjera).

4. Odpowiadaj zawsze natychmiast, podając wynik działania narzędzia. Nie mów klientowi, że 
coś będzie sprawdzone później ani żeby czekał.

5. Jeśli brakuje jakiejś informacji potrzebnej do rezerwacji, poproś klienta **tylko o 
brakującą informację**.

6. Jeśli termin jest zajęty lub klient nie podał preferencji, dostosuj odpowiedź zgodnie z 
powyższymi zasadami.
"""

tools  = [
    {
        "type": "function",
        "function": {
            "name": "create_booking",
            "description": "Tworzy rezereację wizyty do barbera. Funkcja powinna być użyta dopiero po sprawdzeniu dostępności terminu za pomocą narzędzia check_availability.",
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
                    "hairdresser_name": {"type": "string", "description": "Imię fryzjera, jeśli klient wskazał konkretnego"},
                    "date": {"type": "string", "description": "Data w formacie: YYYY-MM-DD"},
                    "time": {"type": "string", "description": "Godzina wizyty w formacie HH:MM"},
                    "service_name": {"type": "string", "description": "Nazwa usługi"}
                },
                "required": ["date", "time", "service_name"]
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