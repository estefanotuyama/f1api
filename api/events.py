from fastapi import APIRouter
from crud.event import get_events_from_year
from db.db_utils import SessionDep

router = APIRouter()

@router.get("/events/{year}")
def read_events(year: int, session: SessionDep):
    return get_events_from_year(session, year)
