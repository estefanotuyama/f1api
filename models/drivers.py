from sqlalchemy import PrimaryKeyConstraint
from sqlmodel import SQLModel, Field


# Classe que contém a modelação da tabela de drivers

class Driver(SQLModel, table=True):
    session_key: int = Field(index=True)
    first_name: str
    last_name: str
    name_acronym: str = Field(index=True)
    number: int
    team: str
    headshot_url: str
    __table_args__ = (PrimaryKeyConstraint("name_acronym", "session_key"),)