from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, UniqueConstraint, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base

class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)

class Hairdresser(Base):
    __tablename__ = "hairdressers"

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    specialization = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True)
    hairdresser_id = Column(Integer, ForeignKey("hairdressers.id"))
    service_id = Column(Integer, ForeignKey("services.id"))
    client_name = Column(String, nullable=False)
    client_phone = Column(String, nullable=False)
    booking_datetime = Column(DateTime, nullable=False)
    status = Column(String, default="scheduled")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    notes = Column(String(500), nullable=True)

    __table_args__ = (
        UniqueConstraint("hairdresser_id", "booking_datetime"),
    )

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

class Conversation(Base):
    __tablename__ = "conversations"

    conversation_id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class Message(Base):
    __tablename__ = "messages"

    message_id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("conversations.conversation_id"))
    role = Column(String)
    content = Column(Text)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))