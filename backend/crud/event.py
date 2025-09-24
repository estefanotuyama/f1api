from sqlmodel import Session, select
from backend.models.events import Event
from backend.models.teams import Teams


def get_events_from_year(session:Session, year: int):
    """
    Queries the database to find all F1 events in a given year.
    :param session: Database session, not related to an F1 session.
    :param year: Year for which you want to find events
    :return: List of events as 'Event' pydantic model.
    """
    return session.exec(select(Event).where(Event.year == year)).all()

def get_available_years(session):
    """
    Queries database to find all unique years so we can display them to users.
    :param session: Database session
    :return: Set with all years.
    """
    years = session.exec(select(Event.year)).all()
    return sorted(set(years))

def get_teams(session):
    teams = session.exec(select(Teams)).all()

    team_map = {team.name : team.color for team in teams}
    return team_map
