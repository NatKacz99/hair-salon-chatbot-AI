from starlette.datastructures import CommaSeparatedStrings
from app import models
from sqlalchemy.orm import Session
from datetime import datetime
from app.routers.bookings import get_available_slots
from sqlalchemy.exc import IntegrityError

def create_booking_from_chat(args: dict, db: Session) -> dict:
    service = db.query(models.Service).filter(
        models.Service.name.ilike(args["service_name"])
    ).first()

    if not service:
        return {
            "status": "service_not_found",
            "provided_name": args["service_name"]
        }

    booking_datetime = datetime.fromisoformat(args["booking_datetime"])

    hairdresser = None
    hairdresser_name = args.get("hairdresser_name")

    # if the hairdresser was given
    if hairdresser_name:
        hairdresser = db.query(models.Hairdresser).filter(
            models.Hairdresser.first_name.ilike(hairdresser_name)
        ).first()

        if not hairdresser:
            return {
                "status": "hairdresser_not_found",
                "provided_name": hairdresser_name
            }

        slots = get_available_slots(
        hairdresser_id=hairdresser.id,
        date=booking_datetime.date(),
        service_id=service.id,
        db=db
        )   

        if booking_datetime.strftime("%H:%M") not in slots["free_hours"]:
            return {
                "status": "slot_take",
                "requested_time": booking_datetime.strftime("%H:%M"),
                "date": booking_datetime.strftime("%d.%m.%Y"),
                "hairdresser": hairdresser.first_name,
                "free_hours": slots["free_hours"]
            }
    
    # if the hairdresser was not given
    else:
        hairdressers = db.query(models.Hairdresser).all()

        for available_hairdresser in hairdressers:
            slots = get_available_slots(
                hairdresser_id=available_hairdresser.id,
                date=booking_datetime.date(),
                service_id=service.id,
                db=db
            )

            if booking_datetime.strftime("%H:%M") in slots["free_hours"]:
                hairdresser = available_hairdresser
                break

        if not hairdresser:
            return {
                "status": "not_available_hairdresser",
                "requested_time": booking_datetime.strftime("%H:%M"),
                "date": booking_datetime.strftime("%d.%m.%Y")
            }

    try:
        booking = models.Booking(
            client_name=args["client_name"],
            client_phone=args["client_phone"],
            hairdresser_id=hairdresser.id,
            service_id=service.id,
            booking_datetime=booking_datetime,
            notes=args.get("notes")
        )

        db.add(booking)
        db.commit()
        db.refresh(booking)

        return {
            "status": "success",
            "booking_datetime": booking_datetime.strftime("%d.%m.%Y %H:%M"),
            "hairdresser": hairdresser.first_name,
            "client_name": args["client_name"]
        }

    except IntegrityError:
        db.rollback()

        slots = get_available_slots(
            hairdresser_id=hairdresser.id,
            date=booking_datetime.date(),
            service_id=service.id,
            db=db
        )

        return {
            "status": "slot_taken",
            "requested_time": booking_datetime.strftime("%H:%M"),
            "date": booking_datetime.strftime("%d.%m.%Y"),
            "hairdresser": hairdresser.first_name,
            "free_hours": slots["free_hours"]
        }

def check_availability_from_chat(args: dict, db: Session) -> dict:
    hairdresser = db.query(models.Hairdresser).filter(
        models.Hairdresser.first_name.ilike(args["hairdresser_name"])
    ).first()

    if not hairdresser:
        return {
            "status": "hairdresser_not_found",
            "provided_name": args["hairdresser_name"]
        }

    service = db.query(models.Service).filter(
        models.Service.name.ilike(args["service_name"])
    ).first()

    if not service:
        return {
            "status": "service_not_found",
            "provided_name": args["service_name"]
        }

    slots = get_available_slots(
        hairdresser_id=hairdresser.id,
        date=args["date"],
        service_id=service.id,
        db=db
    )

    if not slots["free_hours"]:
        return {
            "status": "no_slots",
            "date": args["date"],
            "hairdresser": hairdresser.first_name
        }

    return {
        "status": "success",
        "date": args["date"],
        "hairdresser": hairdresser.first_name,
        "free_hours": slots["free_hours"]
    }

def cancel_booking_from_chat(args: dict, db: Session) -> dict:
    booking_datetime = datetime.fromisoformat(args["booking_datetime"])

    booking = db.query(models.Booking).filter(
        models.Booking.client_phone == args['client_phone'],
        models.Booking.booking_datetime == booking_datetime
    ).first()

    if not booking:
        return {
            "status": "booking_not_found",
            "client_phone": args["client_phone"],
            "booking_datetime": booking_datetime.strftime("%d.%m.%Y %H:%M")
        }

    if booking.status == "cancelled":
        return {
            "status": "already_cancelled",
            "booking_datetime": booking_datetime.strftime("%d.%m.%Y %H:%M")
        }

    booking.status = "cancelled"
    db.commit()

    return {
        "status": "success",
        "booking_datetime": booking_datetime.strftime("%d.%m.%Y %H:%M"),
        "hairdresser": booking.hairdresser_id
    }