from fastapi import APIRouter
from backend.crud.event import get_events_from_year, get_available_years
from backend.db.db_utils import SessionDep

router = APIRouter()

@router.get("/events/{year}",
            summary="Gets F1 events",
            description="Accesses de DB and returns all F1 events in a year."
)
def read_events(session: SessionDep, year: int):
    return get_events_from_year(session, year)

@router.get("/events/years/",
            summary="Gets all years that we have data for",
            description="Accesses de DB and returns all years for which we have data.")
def read_available_years(session: SessionDep):
    return get_available_years(session)