from typing import Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import SQLModel, Field, null

"""
Database model that represents a Lap a driver completed in a session.
"""

class SessionLaps(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    driver_id: int = Field(index=True, foreign_key="driver.id")
    session_key: int = Field(index=True, foreign_key="f1session.session_key")
    lap_number: int
    is_pit_out_lap: bool
    lap_time: float = Field(default=0.0, nullable=True)
    st_speed: int = Field(default=0, nullable=True)
    compound: Optional[str] = Field(default=None, nullable=True)
    __table_args__ = (
        UniqueConstraint("driver_id", "session_key", "lap_number",name="uq_lap"),
    )
