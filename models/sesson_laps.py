from sqlmodel import SQLModel, Field


class SessionLaps(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    driver_acronym: str = Field(index=True)
    session_key: int = Field(index=True)
    lap_number: int
    lap_time: float
    compound: str