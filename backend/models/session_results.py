from sqlmodel import SQLModel, Field

"""
Database model that Represents an F1Session's result (work in progress, still need to populate this)
"""

class SessionResults(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    session_key: int = Field(index=True)
    session_type: str