from crud.lap import get_driver_lap_times
from db.database import get_session

def test_read_driver_laps():
    with next(get_session()) as session:
        lap_times = get_driver_lap_times(session, 9519, 16)
        assert lap_times is not None
        print(f"Lap times: {lap_times}")