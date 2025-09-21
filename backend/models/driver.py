from sqlalchemy import Column, Integer, UniqueConstraint
from sqlmodel import SQLModel, Field, null


"""
Database model that Represents a unique driver in the database.
"""

class Driver(SQLModel, table=True):
    id: int = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    driver_number: int
    first_name: str
    last_name: str
    name_acronym: str
    headshot_url: str = Field(default="", nullable=True)
    __table_args__ = (UniqueConstraint("first_name", "last_name", "name_acronym"),)
