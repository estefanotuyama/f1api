from sqlmodel import Session, select
from models.events import Event


def get_events_from_year(session:Session, year: int):
    return session.exec(select(Event).where(Event.year == year)).all()