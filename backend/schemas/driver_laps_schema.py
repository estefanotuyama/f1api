from typing import List
from pydantic import BaseModel

"""
This is a response model used by the application so that we can correctly return all
laps a driver completed in a session.
"""

class LapRead(BaseModel):
    lap_number: int
    time: float
    speed_trap: int
    is_pit_out_lap: bool
    compound: str

class DriverLapsRead(BaseModel):
    driver_number: int
    first_name: str
    last_name: str
    team: str
    headshot_url: str
    laps: List[LapRead]
    class Config:
        orm_mode = True
