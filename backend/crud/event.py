from sqlmodel import Session, select
from backend.models.events import Event


def get_events_from_year(session:Session, year: int):
    """
    Queries the database to find all F1 events in a given year.
    :param session: Database session, not related to an F1 session.
    :param year: Year for which you want to find events
    :return: List of events as 'Event' pydantic model.
    """
    return session.exec(select(Event).where(Event.year == year)).all()