from sqlmodel import Session, select
from models.session_laps import SessionLaps
from crud.driver import get_single_driver_from_session_key


def get_driver_lap_times(session: Session, session_key: int, driver_number: int):
    driver = get_single_driver_from_session_key(session, session_key, driver_number)

    laps = session.exec(select(SessionLaps).where(
        (SessionLaps.driver_number == driver.number) & (SessionLaps.session_key == driver.session_key)
    )).all()
    return driver, laps