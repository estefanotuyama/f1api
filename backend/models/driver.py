from sqlalchemy import Column, Integer, UniqueConstraint
from sqlmodel import SQLModel, Field, null


"""
Database model that Represents a unique driver in the database.
"""

class Driver(SQLModel, table=True):
    id: int = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    first_name: str = Field(default="")
    last_name: str = Field(default="")
    name_acronym: str = Field(unique=True)
    headshot_url: str = Field(default="")
