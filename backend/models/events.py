from sqlmodel import SQLModel, Field

"""
Database model that represents an Event in formula 1 (A grand prix weekend or testing weekend).
"""

class Event(SQLModel, table=True):
    meeting_key: int = Field(primary_key=True)
    circuit_key: int
    location: str
    country_name: str
    circuit_name: str
    meeting_official_name: str
    year: int = Field(index=True)
