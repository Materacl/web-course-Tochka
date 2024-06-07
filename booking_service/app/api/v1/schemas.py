from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class User(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    is_admin: bool

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class FilmCreate(BaseModel):
    title: str
    description: str


class Film(BaseModel):
    id: int
    title: str
    description: str

    class Config:
        orm_mode = True


class CinemaHallCreate(BaseModel):
    name: str
    capacity: int


class CinemaHall(BaseModel):
    id: int
    name: str
    capacity: int

    class Config:
        orm_mode = True


class SessionCreate(BaseModel):
    film_id: int
    datetime: datetime
    price: float
    cinema_hall_id: int


class Session(BaseModel):
    id: int
    film_id: int
    datetime: datetime
    price: float
    film: Film
    cinema_hall: CinemaHall

    class Config:
        orm_mode = True


class SeatCreate(BaseModel):
    session_id: int
    seat_number: str


class Seat(BaseModel):
    id: int
    session_id: int
    seat_number: str
    is_available: bool

    class Config:
        orm_mode = True


class ReservationCreate(BaseModel):
    booking_id: int
    seat_id: int


class Reservation(BaseModel):
    id: int
    booking_id: int
    seat_id: int
    status: str
    deadline: datetime

    class Config:
        orm_mode = True


class BookingCreate(BaseModel):
    session_id: int


class Booking(BaseModel):
    id: int
    session_id: int
    user_id: int | None
    status: str
    reservations: List[Reservation]

    class Config:
        orm_mode = True


class AdminAction(BaseModel):
    status: str
