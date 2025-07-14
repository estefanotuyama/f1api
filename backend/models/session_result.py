from sqlalchemy import PrimaryKeyConstraint
from typing import Union, List, Optional
from sqlmodel import SQLModel, Field


"""
Database model that Represents an F1Session's result (work in progress, still need to populate this)
"""


class SessionResult(SQLModel, table=True):
    meeting_key: int
    session_key: int = Field(index=True)
    driver_number: int = Field(index=True)
    position: Optional[int] = Field(default=None)
    duration: Optional[str] = Field(default=None)
    number_of_laps: Optional[int] = Field(default=None)
    gap_to_leader: Optional[str] = Field(default=None)
    dnf: bool = Field(default=False)
    dns: bool = Field(default=False)
    dsq: bool = Field(default=False)

    __table_args__ = (
        PrimaryKeyConstraint("session_key", "driver_number"),
    )