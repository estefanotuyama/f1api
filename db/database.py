from sqlmodel import Session, create_engine, SQLModel

sqlite_url = "sqlite:///db/f1.db"
engine = create_engine(sqlite_url, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

def create_db_and_tables(populating):
    SQLModel.metadata.create_all(engine)
    if populating:
        from db_populate import populate_db
        populate_db()