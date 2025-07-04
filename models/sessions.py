from sqlmodel import SQLModel, Field


class F1Session(SQLModel, table=True):
    location: str
    meeting_key: int = Field(index=True)
    session_key: int = Field(index=True, primary_key=True)
    session_type: str
    session_name: str
    date: str