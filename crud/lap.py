from sqlmodel import Session, select
from models.session_laps import SessionLaps
from crud.driver import get_single_driver_from_session_key

# queremos pegar um numero de piloto e a session key, e retornar todas as laps do piloto naquela sessão, no formato json
"""
{
    {
        'driver_number': int
        'first_name': str,
        'last_name': str,
        'team': str
        'laps': [
            1:{
                'time':int,
                'speed_trap':int,
                'is_pit_out_lap':bool,
                'compound':str
            },
            2:{
                'time':int,
                'speed_trap':int,
                'is_pit_out_lap':bool,
                'compound':str
            }
        ]
    }
}

simple:
{
    'driver_number': int,
    'first_name': str,
    'last_name': str,
    'team': str,
    'headshot_url': str,
    'laps': [{}]
}
"""
def get_driver_lap_times(session: Session, session_key: int, driver_number: int):
    driver = get_single_driver_from_session_key(session, session_key, driver_number)

    laps = session.exec(select(SessionLaps).where(
        (SessionLaps.driver_number == driver.number) & (SessionLaps.session_key == driver.session_key)
    )).all()
    return driver, laps