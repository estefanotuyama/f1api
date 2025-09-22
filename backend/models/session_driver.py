from sqlalchemy import PrimaryKeyConstraint
from sqlmodel import SQLModel, Field


"""
Database model that Represents a driver's participation in a session.
"""

class SessionDriver(SQLModel, table=True):
    session_key: int = Field(index=True, foreign_key="f1session.session_key")
    driver_id: int = Field(index=True, foreign_key="driver.id")
    team: str = Field(default="")
    driver_number: int
    __table_args__ = (PrimaryKeyConstraint("session_key", "driver_id"),)
