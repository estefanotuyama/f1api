from sqlmodel import Session, select
from backend.models.sessions import F1Session

def get_sessions_from_meeting_key(meeting_key: int, session: Session):
    return session.exec(select(F1Session).where(F1Session.meeting_key == meeting_key)).all()