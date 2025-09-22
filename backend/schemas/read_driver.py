from pydantic import BaseModel

class DriverSessionInfo(BaseModel):
    driver_number: int
    team: str | None = None
    first_name: str
    last_name: str
    name_acronym: str
    headshot_url: str
