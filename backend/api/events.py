from fastapi import APIRouter
from backend.crud.event import get_events_from_year
from backend.db.db_utils import SessionDep

router = APIRouter()

@router.get("/events/{year}")
def read_events(session: SessionDep, year: int):
    return get_events_from_year(session, year)
