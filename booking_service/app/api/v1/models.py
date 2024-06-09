from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Float, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base
from enum import Enum as PyEnum


class FilmStatus(str, PyEnum):
    AVAILABLE = "available"
    NOT_AVAILABLE = "not_available"


class SessionStatus(str, PyEnum):
    UPCOMING = "upcoming"
    NOW_PLAYING = "now_playing"
    COMPLETED = "completed"
    CANCELED = "canceled"


class BookingStatus(str, PyEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELED = "canceled"


class ReservationStatus(str, PyEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELED = "canceled"


class SeatStatus(str, PyEnum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    CANCELED = "canceled"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    nickname = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    bookings = relationship("Booking", back_populates="user", cascade="all, delete-orphan")


class Film(Base):
    __tablename__ = "films"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    duration = Column(Integer)
    image_url = Column(String, nullable=True)
    status = Column(Enum(FilmStatus), default=FilmStatus.AVAILABLE)
    sessions = relationship("Session", back_populates="film", cascade="all, delete-orphan")


class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index=True)
    film_id = Column(Integer, ForeignKey("films.id", ondelete="CASCADE"))
    datetime = Column(DateTime, index=True)
    price = Column(Float)
    capacity = Column(Integer)
    auto_booking = Column(Boolean, default=False)
    status = Column(Enum(SessionStatus), default=SessionStatus.UPCOMING)
    film = relationship("Film", back_populates="sessions")
    bookings = relationship("Booking", back_populates="session", cascade="all, delete-orphan")
    seats = relationship("Seat", back_populates="session", cascade="all, delete-orphan")


class Seat(Base):
    __tablename__ = "seats"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"))
    reservation_id = Column(Integer, ForeignKey("reservations.id", ondelete="SET NULL"))
    status = Column(Enum(SeatStatus), default=FilmStatus.AVAILABLE)
    session = relationship("Session", back_populates="seats")


class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING)
    session = relationship("Session", back_populates="bookings")
    user = relationship("User", back_populates="bookings")
    reservations = relationship("Reservation", back_populates="booking", cascade="all, delete-orphan")


class Reservation(Base):
    __tablename__ = "reservations"
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id", ondelete="CASCADE"))
    seat_id = Column(Integer, ForeignKey("seats.id", ondelete="SET NULL"))
    status = Column(Enum(ReservationStatus), default=ReservationStatus.PENDING)
    deadline = Column(DateTime, default=datetime.utcnow)
    booking = relationship("Booking", back_populates="reservations")
