from sqlalchemy import PrimaryKeyConstraint
from sqlmodel import SQLModel, Field


# Classe que contém a modelação da tabela de drivers

class Driver(SQLModel, table=True):
    name: str
    last_name: str
    name_acronym: str = Field(index=True)
    number: int
    team: str
    year: int = Field(index=True)
    __table_args__ = (PrimaryKeyConstraint("acronym", "year"),)