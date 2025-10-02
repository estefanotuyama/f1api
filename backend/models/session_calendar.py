from datetime import datetime
from sqlmodel import SQLModel, Field

class SessionCalendar(SQLModel, table=True):
    summary: str | None = None
    start: datetime = Field(primary_key=True, index=True)
    end: datetime = Field(primary_key=True, index=True)
    location: str | None = None
