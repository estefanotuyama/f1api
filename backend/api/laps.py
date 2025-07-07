from fastapi import APIRouter

from backend.crud.lap import get_driver_lap_times
from backend.db.db_utils import SessionDep
from backend.schemas.driver_laps_schema import DriverLapsRead, LapRead

router = APIRouter()

@router.get("/laps/{session_key}/{driver_number}", response_model=DriverLapsRead)
def read_driver_session_laps(session:SessionDep, session_key:int, driver_number:int):
    driver, laps = get_driver_lap_times(session, session_key, driver_number)

    driver_laps = DriverLapsRead(
        driver_number=driver.number,
        first_name=driver.first_name,
        last_name=driver.last_name,
        team=driver.team,
        headshot_url=driver.headshot_url,
        laps = [
            LapRead(
                lap_number=lap.lap_number,
                time = lap.lap_time,
                speed_trap= lap.st_speed,
                is_pit_out_lap=lap.is_pit_out_lap,
                compound=lap.compound or "Not Provided" #todo: derive compound since we don't know from the API
            )
            for lap in laps
        ]
    )
    return driver_laps