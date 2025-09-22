from sqlmodel import Session, select
from backend.crud.driver import get_drivers_from_session_key
from backend.models import session_result
from backend.models.driver import Driver
from backend.models.session_driver import SessionDriver
from backend.models.session_result import SessionResult
from backend.models.sessions import F1Session

def get_sessions_from_meeting_key(session:Session, meeting_key:int):
    """
    Queries the db for all F1 sessions in an F1 event.
    :param session: Database session, not related to an F1 session.
    :param meeting_key: Unique key identifying an event.
    :return: List of sessions as 'F1Session' pydantic model.
    """
    return session.exec(select(F1Session).where(F1Session.meeting_key == meeting_key)).all()

def get_session_result(session: Session, session_key: int):

    session_drivers = get_drivers_from_session_key(session, session_key)
    session_result = session.execute(select(SessionResult).where(SessionResult.session_key == session_key)).all()

    
