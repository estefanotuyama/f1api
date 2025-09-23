import json
from pydantic import BaseModel, field_validator

class DriverPosition(BaseModel):
    position: int | None = None
    team: str
    first_name: str
    last_name: str
    number_of_laps: int
    gap_to_leader: float | str | None = None
    duration: float | None = 0.0
    dnf: bool
    dns: bool
    dsq: bool

    @field_validator('duration', mode='before')
    @classmethod
    def parse_duration(cls, v):
        if v == 'None' or v == '' or v is None:
            return None

        if isinstance(v, str) and v.startswith('['):
            try:
                values = json.loads(v)
                for val in reversed(values):
                    if val is not None:
                        return float(val)
                return None
            except (json.JSONDecodeError, ValueError):
                return None

        print(v)
        return float(v)

    @field_validator('gap_to_leader', mode='before')
    @classmethod
    def parse_gap_to_leader(cls, v):
        if v == 'None' or v == '' or v is None:
            return None

        if isinstance(v, str) and v.startswith('['):
            try:
                values = json.loads(v)
                for val in reversed(values):
                    if val is not None:
                        return float(val)
                return None
            except (json.JSONDecodeError, ValueError):
                return None


        return v

class ReadSessionResult(BaseModel):
    result: list[DriverPosition]
