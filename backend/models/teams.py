from sqlmodel import Field, SQLModel, table


class Teams(SQLModel, table=True):
    name: str = Field(primary_key=True)
    color: str

