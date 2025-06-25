from fastapi import APIRouter
from db.db_utils import SessionDep
from crud.f1session import get_sessions_from_meeting_key

router = APIRouter()

@router.get('/sessions/{meeting_key}')
def read_sessions(meeting_key: int, session: SessionDep):
    return get_sessions_from_meeting_key(meeting_key, session)