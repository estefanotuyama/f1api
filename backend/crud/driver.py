from sqlmodel import Session, select
from backend.models.drivers import Driver

def get_drivers_from_session_key(session:Session, session_key:int):
    """
    Queries the database to find all drivers that participated in a f1 session.
    :param session: The database session, not related to an F1 session.
    :param session_key: Unique key identifying the session (FP1, Quali, Race, etc.)
    :return: a list of drivers as pydantic 'Driver' models.
    """
    return session.exec(select(Driver).where(Driver.session_key == session_key)).all()

def get_single_driver_from_session_key(session:Session, session_key:int, driver_number:int):
    """
    Queries the database to find a driver that participated in a session.
    :param session: The database session, not related to an F1 session.
    :param session_key: Unique key identifying the session (FP1, Quali, Race, etc.)
    :param driver_number: Driver's number in Formula 1. (Example Charles LeClerc = 16)
    :return: the driver as a pydantic 'Driver' model.
    """
    return session.exec(select(Driver).where(
        (Driver.session_key == session_key) & (Driver.number == driver_number)
    )).first()