from sqlmodel import SQLModel, Field


class Event(SQLModel, table=True):
    meeting_key: int = Field(primary_key=True)
    circuit_key: int
    location: str
    country_name: str
    circuit_name: str
    meeting_official_name: str
    year: int = Field(index=True)
