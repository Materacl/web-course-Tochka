from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    reservations = relationship("Reservation", back_populates="user")


class Film(Base):
    __tablename__ = "films"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    sessions = relationship("Session", back_populates="film")


class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index=True)
    film_id = Column(Integer, ForeignKey("films.id"))
    datetime = Column(DateTime, index=True)
    price = Column(Float)
    film = relationship("Film", back_populates="sessions")
    seats = relationship("Seat", back_populates="session")
    cinema_hall_id = Column(Integer, ForeignKey("cinema_halls.id"))
    cinema_hall = relationship("CinemaHall", back_populates="sessions")


class CinemaHall(Base):
    __tablename__ = "cinema_halls"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    capacity = Column(Integer)
    sessions = relationship("Session", back_populates="cinema_hall")


class Seat(Base):
    __tablename__ = "seats"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    seat_number = Column(String, index=True)
    is_available = Column(Boolean, default=True)
    session = relationship("Session", back_populates="seats")


class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default="pending")  # pending, confirmed, canceled
    session = relationship("Session")
    user = relationship("User")
    reservations = relationship("Reservation", back_populates="booking")


class Reservation(Base):
    __tablename__ = "reservations"
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"))
    seat_id = Column(Integer, ForeignKey("seats.id"))
    status = Column(String, default="pending")  # pending, confirmed, canceled
    deadline = Column(DateTime, default=datetime.utcnow)
    booking = relationship("Booking", back_populates="reservations")
    seat = relationship("Seat")
