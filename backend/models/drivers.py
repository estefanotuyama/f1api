from sqlalchemy import PrimaryKeyConstraint
from sqlmodel import SQLModel, Field


"""
Database model that Represents a driver entry in the database.
"""

class Driver(SQLModel, table=True):
    session_key: int = Field(index=True)
    first_name: str
    last_name: str
    name_acronym: str
    number: int = Field(index=True)
    team: str
    headshot_url: str
    __table_args__ = (PrimaryKeyConstraint("name_acronym", "session_key"),)