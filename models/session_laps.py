from typing import Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import SQLModel, Field


class SessionLaps(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    driver_number: int = Field(index=True)
    session_key: int = Field(index=True)
    lap_number: int
    is_pit_out_lap: bool
    lap_time: float
    st_speed: int
    compound: Optional[str] = Field(default=None, nullable=True)
    __table_args__ = (
        UniqueConstraint("driver_number", "session_key", "lap_number",name="uq_lap"),
    )