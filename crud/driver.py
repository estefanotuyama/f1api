from sqlmodel import Session, select
from models.drivers import Driver

def get_drivers_from_session_key(session:Session, session_key:int):
    return session.exec(select(Driver).where(Driver.session_key == session_key)).all()

def get_single_driver_from_session_key(session:Session, session_key:int, driver_number:int):
    return session.exec(select(Driver).where(
        (Driver.session_key == session_key) & (Driver.number == driver_number)
    )).first()