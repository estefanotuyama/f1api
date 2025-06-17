from email.policy import default

from sqlmodel import SQLModel, Field


class SessionResults(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    session_key: int = Field(index=True)
    session_type: str