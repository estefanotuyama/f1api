from sqlmodel import SQLModel, Field


class Session(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    session_key: int = Field(index=True)
    session_type: str