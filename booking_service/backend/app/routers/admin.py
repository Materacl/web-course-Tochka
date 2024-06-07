from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User as UserModel
from app.schemas import FilmCreate, Film, SessionCreate, Session, User, Reservation, CinemaHallCreate, CinemaHall
from app.crud import get_reservations, update_reservation_status, create_cinema_hall
from app.utils.auth import get_current_active_admin
from app.crud import create_film, create_session, get_films, get_sessions

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(get_current_active_admin)],
)


@router.put("/users/{user_id}/set_admin", response_model=User)
def set_user_admin(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_admin = True
    db.commit()
    db.refresh(user)
    return user


@router.post("/reservations/{reservation_id}/confirm", response_model=Reservation)
def admin_confirm_reservation(reservation_id: int,
                              db: Session = Depends(get_db)):
    return update_reservation_status(db, reservation_id=reservation_id, status="confirmed")


@router.post("/reservations/{reservation_id}/cancel", response_model=Reservation)
def admin_cancel_reservation(reservation_id: int,
                             db: Session = Depends(get_db)):
    return update_reservation_status(db, reservation_id=reservation_id, status="canceled")


@router.post("/films/", response_model=Film)
def create_new_film(film: FilmCreate, db: Session = Depends(get_db)):
    return create_film(db=db, film=film)


@router.post("/sessions/", response_model=Session)
def create_new_session(session: SessionCreate, db: Session = Depends(get_db)):
    return create_session(db=db, session=session)


@router.post("/cinema_halls/", response_model=CinemaHall)
def create_new_cinema_hall(cinema_hall: CinemaHallCreate, db: Session = Depends(get_db)):
    return create_cinema_hall(db=db, cinema_hall=cinema_hall)
