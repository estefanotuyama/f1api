from pydantic import BaseModel

class DriverPosition(BaseModel):
    position: int
    team: str
    first_name: str
    last_name: str
    num_of_laps: int
    gap_to_leader: float
    duration: float

class ReadSessionResult(BaseModel):
    event_name: str
    result: list[DriverPosition]
