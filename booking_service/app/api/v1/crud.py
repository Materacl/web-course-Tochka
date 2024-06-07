from sqlalchemy.orm import Session
from .models import User, Film, Session as FilmSession, Seat, Booking, Reservation, CinemaHall
from .schemas import UserCreate, FilmCreate, SessionCreate, SeatCreate, BookingCreate, ReservationCreate, \
    CinemaHallCreate


def create_user(db: Session, user: UserCreate):
    db_user = User(email=user.email, hashed_password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def create_film(db: Session, film: FilmCreate):
    db_film = Film(**film.dict())
    db.add(db_film)
    db.commit()
    db.refresh(db_film)
    return db_film


def get_film(db: Session, film_id: int):
    return db.query(Film).filter(Film.id == film_id).first()


def get_films(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Film).offset(skip).limit(limit).all()


def create_session(db: Session, session: SessionCreate):
    db_session = FilmSession(**session.dict())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)

    cinema_hall = db.query(CinemaHall).filter(CinemaHall.id == session.cinema_hall_id).first()
    for seat_number in range(1, cinema_hall.capacity + 1):
        seat = Seat(
            session_id=db_session.id,
            seat_number=str(seat_number)
        )
        db.add(seat)
    db.commit()

    return db_session


def create_cinema_hall(db: Session, cinema_hall: CinemaHallCreate):
    db_cinema_hall = CinemaHall(**cinema_hall.dict())
    db.add(db_cinema_hall)
    db.commit()
    db.refresh(db_cinema_hall)
    return db_cinema_hall


def get_cinema_hall(db: Session, cinema_hall_id: int):
    return db.query(CinemaHall).filter(CinemaHall.id == cinema_hall_id).first()


def get_cinema_halls(db: Session, skip: int = 0, limit: int = 10):
    return db.query(CinemaHall).offset(skip).limit(limit).all()


def get_session(db: Session, session_id: int):
    return db.query(FilmSession).filter(FilmSession.id == session_id).first()


def get_sessions(db: Session, skip: int = 0, limit: int = 10):
    return db.query(FilmSession).offset(skip).limit(limit).all()


def create_seat(db: Session, seat: SeatCreate):
    db_seat = Seat(**seat.dict())
    db.add(db_seat)
    db.commit()
    db.refresh(db_seat)
    return db_seat


def get_seat(db: Session, seat_id: int):
    return db.query(Seat).filter(Seat.id == seat_id).first()


def get_seats(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Seat).offset(skip).limit(limit).all()


def create_booking(db: Session, booking: BookingCreate, user_id: int):
    db_booking = Booking(**booking.dict(), user_id=user_id)
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking


def get_booking(db: Session, booking_id: int):
    return db.query(Booking).filter(Booking.id == booking_id).first()


def get_bookings(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Booking).offset(skip).limit(limit).all()


def get_user_bookings(db: Session, user_id: int, skip: int = 0, limit: int = 10):
    print(db.query(Booking).filter(Booking.user_id == user_id).all())
    return db.query(Booking).filter(Booking.user_id == user_id).offset(skip).limit(limit).all()


def delete_booking(db: Session, booking_id: int):
    db_booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if db_booking:
        db.query(Reservation).filter(Reservation.booking_id == booking_id).delete()
        db.delete(db_booking)
        db.commit()
    return db_booking


def update_booking_status(db: Session, booking_id: int, status: str):
    db_booking = get_booking(db, booking_id)
    if db_booking:
        db_booking.status = status
        db.commit()
        db.refresh(db_booking)
    return db_booking


def create_reservation(db: Session, reservation: ReservationCreate):
    db_reservation = Reservation(**reservation.dict())
    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)
    return db_reservation


def get_reservation(db: Session, reservation_id: int):
    return db.query(Reservation).filter(Reservation.id == reservation_id).first()


def get_reservations(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Reservation).offset(skip).limit(limit).all()


def update_reservation_status(db: Session, reservation_id: int, status: str):
    db_reservation = get_reservation(db, reservation_id)
    if db_reservation:
        db_reservation.status = status
        db.commit()
        db.refresh(db_reservation)
    return db_reservation


def get_unconfirmed_reservations(db: Session):
    return db.query(Reservation).filter(Reservation.status == "pending").all()
