from fastapi import APIRouter
from db.db_utils import SessionDep
from crud.driver import get_drivers_from_session_key

router = APIRouter()

@router.get('/drivers/{session_key}')
def read_drivers_in_session(session: SessionDep, session_key: int):
    return get_drivers_from_session_key(session, session_key)