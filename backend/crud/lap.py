from sqlmodel import Session, select
from backend.models.session_laps import SessionLaps
from backend.crud.driver import get_single_driver_from_session_key


def get_driver_lap_times(session: Session, session_key: int, driver_number: int):
    """
    Queries database for all of a driver's lap times in a given F1 session.
    :param session: Database session, not related to an F1 session.
    :param session_key: Unique key identifying the session (FP1, Quali, Race, etc.)
    :param driver_number: Driver's number in Formula 1. (Example Charles LeClerc = 16)
    :return: driver, as a 'Driver' pydantic model, and a list of laps, each a 'SessionLaps' pydantic model.
    """
    driver = get_single_driver_from_session_key(session, session_key, driver_number)

    laps = session.exec(select(SessionLaps).where(
        (SessionLaps.driver_number == driver.number) & (SessionLaps.session_key == driver.session_key)
    )).all()
    return driver, laps