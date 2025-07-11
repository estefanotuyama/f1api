from sqlmodel import Session, select
from backend.models.sessions import F1Session

def get_sessions_from_meeting_key(session:Session, meeting_key:int):
    """
    Queries the db for all F1 sessions in an F1 event.
    :param session: Database session, not related to an F1 session.
    :param meeting_key: Unique key identifying an event.
    :return: List of sessions as 'F1Session' pydantic model.
    """
    return session.exec(select(F1Session).where(F1Session.meeting_key == meeting_key)).all()