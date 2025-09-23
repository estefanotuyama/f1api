import json
from pydantic import BaseModel, field_validator


class DriverPosition(BaseModel):
    position: int | None = None
    team: str
    first_name: str
    last_name: str
    number_of_laps: int
    gap_to_leader: float | str | None = None
    duration: float | str | None = None
    dnf: bool
    dns: bool
    dsq: bool

    @field_validator('duration', 'gap_to_leader', mode='before')
    @classmethod
    def parse_numbers(cls, v):
        if v == 'None' or v == '' or v is None:
            return None
        elif not v.startswith('['):
            return v
        else:
            valid_json_string = v.replace("None", "null")
            duration_array = json.loads(valid_json_string)
            for duration in reversed(duration_array):
                if duration is not None:
                    return duration
            return None


class ReadSessionResult(BaseModel):
    result: list[DriverPosition]
