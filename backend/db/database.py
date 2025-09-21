from sqlmodel import Session, create_engine, SQLModel

postgres_url ="postgresql://estefanotuyama@localhost:5432/f1api" 
engine = create_engine(postgres_url, echo=True)

def get_session():
    """Returns the session that will be used to access the database"""
    with Session(engine) as session:
        yield session

def create_db_and_tables(populating:bool):
    """
    Creates the database and populates if populating is True
    :param: whether you are populating the db or not
    """
    SQLModel.metadata.create_all(engine)
    if populating:
        from .update_db import update_db
        update_db()
