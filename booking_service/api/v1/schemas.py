from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from .models import FilmStatus, PaymentStatus, SeatStatus, ReservationStatus, SessionStatus


class UserCreate(BaseModel):
    """
    Schema for creating a new user.
    """
    email: EmailStr
    password: str


class User(BaseModel):
    """
    Schema for representing a user.
    """
    id: int
    email: EmailStr
    nickname: Optional[str] = None
    is_active: bool
    is_admin: bool
    notifications: bool

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    """
    Schema for user login.
    """
    email: EmailStr
    password: str


class SeatCreate(BaseModel):
    """
    Schema for creating a new seat.
    """
    session_id: int


class Seat(BaseModel):
    """
    Schema for representing a seat.
    """
    id: int
    session_id: int
    user_id: Optional[int] = None
    status: SeatStatus

    class Config:
        orm_mode = True


class ReservationCreate(BaseModel):
    """
    Schema for creating a new reservation.
    """
    booking_id: int
    seat_id: int


class Reservation(BaseModel):
    """
    Schema for representing a reservation.
    """
    id: int
    booking_id: int
    seat_id: int
    status: ReservationStatus
    deadline: datetime

    class Config:
        orm_mode = True


class PaymentCreate(BaseModel):
    """
    Schema for creating a new payment.
    """
    id: str
    booking_id: int


class Payment(BaseModel):
    """
    Schema for representing a payment.
    """
    id: str
    booking_id: int
    amount: float
    status: PaymentStatus
    timestamp: datetime

    class Config:
        orm_mode = True


class BookingCreate(BaseModel):
    """
    Schema for creating a new booking.
    """
    session_id: int


class Booking(BaseModel):
    """
    Schema for representing a booking.
    """
    id: int
    session_id: int
    user_id: int
    status: str
    reservations: List[Reservation]
    payments: Optional[List[Payment]]

    class Config:
        orm_mode = True


class SessionCreate(BaseModel):
    """
    Schema for creating a new session.
    """
    film_id: int
    datetime: datetime
    price: float
    capacity: int
    auto_booking: bool


class Session(BaseModel):
    """
    Schema for representing a session.
    """
    id: int
    film_id: int
    datetime: datetime
    price: float
    capacity: int
    auto_booking: bool
    status: SessionStatus
    bookings: List[Booking]
    seats: List[Seat]

    class Config:
        orm_mode = True


class FilmCreate(BaseModel):
    """
    Schema for creating a new film.
    """
    title: str
    description: str
    duration: int
    status: FilmStatus


class Film(BaseModel):
    """
    Schema for representing a film.
    """
    id: int
    title: str
    description: str
    duration: int
    image_url: Optional[str] = None
    status: FilmStatus
    sessions: List[Session]

    class Config:
        orm_mode = True


class AdminAction(BaseModel):
    """
    Schema for representing an admin action.
    """
    status: str
