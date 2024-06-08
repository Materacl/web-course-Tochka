from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

from .models import FilmStatus, SeatStatus, ReservationStatus


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class User(BaseModel):
    id: int
    email: EmailStr
    nickname: Optional[str] = None
    is_active: bool
    is_admin: bool

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class SeatCreate(BaseModel):
    session_id: int


class Seat(BaseModel):
    id: int
    session_id: int
    user_id: Optional[int] = None
    status: SeatStatus

    class Config:
        orm_mode = True


class ReservationCreate(BaseModel):
    booking_id: int
    seat_id: int


class Reservation(BaseModel):
    id: int
    booking_id: int
    seat_id: int
    status: ReservationStatus
    deadline: datetime

    class Config:
        orm_mode = True


class BookingCreate(BaseModel):
    session_id: int


class Booking(BaseModel):
    id: int
    session_id: int
    user_id: int
    status: str
    reservations: List[Reservation]

    class Config:
        orm_mode = True


class SessionCreate(BaseModel):
    film_id: int
    datetime: datetime
    price: float


class Session(BaseModel):
    id: int
    film_id: int
    datetime: datetime
    price: float
    bookings: List[Booking]
    seats: List[Seat]

    class Config:
        orm_mode = True


class FilmCreate(BaseModel):
    title: str
    description: str
    duration: int
    status: FilmStatus


class Film(BaseModel):
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
    status: str
