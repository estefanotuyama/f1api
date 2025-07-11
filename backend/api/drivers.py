from fastapi import APIRouter
from backend.db.db_utils import SessionDep
from backend.crud.driver import get_drivers_from_session_key

router = APIRouter()

@router.get("/drivers/{session_key}",
            summary="Get session drivers",
            description="Accesses the DB and returns all drivers in a given F1 session."
                        "session_key is an Integer that connects a session to everything that pertains it."
)
def read_drivers_in_session(session: SessionDep, session_key: int):
    return get_drivers_from_session_key(session, session_key)