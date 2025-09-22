from sqlmodel import Session, select
from backend.models.driver import Driver
from backend.models.session_driver import SessionDriver
from backend.schemas.read_driver import DriverSessionInfo

def get_drivers_from_session_key(session: Session, session_key: int) -> list[DriverSessionInfo]:
    """
    Queries the database to find all drivers that participated in an F1 session,
    returning a combined data structure with session-specific info.
    """
    statement = (
        select(Driver, SessionDriver)
        .join(SessionDriver)
        .where(SessionDriver.session_key == session_key)
    )

    results = session.exec(statement).all()

    drivers_info = [
        DriverSessionInfo(
            driver_number=session_link.driver_number,
            team=session_link.team,
            
            first_name=driver.first_name,
            last_name=driver.last_name,
            name_acronym=driver.name_acronym,
            headshot_url=driver.headshot_url,
        )
        for driver, session_link in results
    ]

    return drivers_info

def get_single_driver_from_session_key(session:Session, session_key:int, driver_number:int):
    """
    Queries the database to find a driver that participated in a session.
    :param session: The database session, not related to an F1 session.
    :param session_key: Unique key identifying the session (FP1, Quali, Race, etc.)
    :param driver_number: Driver's number in Formula 1. (Example Charles LeClerc = 16)
    :return: the driver as a pydantic 'Driver' model.
    """

    statement = (
        select(Driver, SessionDriver).
        join(SessionDriver).
        where(
            SessionDriver.session_key == session_key,
            SessionDriver.driver_number == driver_number
        )
    )

    return session.exec(statement).first()
