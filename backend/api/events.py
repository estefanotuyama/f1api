from fastapi import APIRouter
from backend.crud.event import get_events_from_year
from backend.db.db_utils import SessionDep

router = APIRouter()

@router.get("/events/{year}",
            summary="Gets F1 events",
            description="Accesses de DB and returns all F1 events in a year."
)
def read_events(session: SessionDep, year: int):
    return get_events_from_year(session, year)
