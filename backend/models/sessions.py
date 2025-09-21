from sqlmodel import SQLModel, Field

"""
Database model that represents a formula 1 session (practice, qualifying, race)
"""

class F1Session(SQLModel, table=True):
    location: str
    meeting_key: int = Field(index=True, foreign_key="event.meeting_key")
    session_key: int = Field(index=True, primary_key=True)
    session_type: str
    session_name: str
    date: str
