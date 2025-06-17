from urllib.request import urlopen
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlmodel import Session
from database import engine
from models.events import Event
import logging
import json

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
URL_BASE = "https://api.openf1.org/v1/"
YEAR='2024'

def get_data(url):
    response = urlopen(url)
    data=json.loads(response.read().decode('utf-8'))
    return data

def populate_db():
    #populate events
    add_events_data()
    logger.info("Events added successfully!")
    #populate

"""
class Driver(SQLModel, table=True):
    name: str
    last_name: str
    name_acronym: str = Field(index=True)
    number: int
    team: str
    year: int = Field(index=True)
    __table_args__ = (PrimaryKeyConstraint("acronym", "year"),)
"""
# DRIVERS POPULATE(2024):


# EVENTS POPULATE(2024)
def add_events_data():
    events_data = get_data(URL_BASE + f'meetings?year={YEAR}')
    with Session(engine) as session:
        for data_point in events_data:
            try:
                event = Event(
                meeting_key=data_point['meeting_key'],
                circuit_key=data_point['circuit_key'],
                location=data_point['location'],
                country_name=data_point['country_name'],
                circuit_name=data_point['circuit_short_name'],
                meeting_official_name=data_point['meeting_official_name'],
                year=data_point['year']
                )
                existing = session.get(Event, data_point["meeting_key"])
                if existing:
                    continue
                session.add(event)
                session.commit()
                logger.info(f"Event added: {data_point['meeting_official_name']}")
            except IntegrityError:
                session.rollback()
                logger.error(f"Duplicate or constraint error for meeting_key={data_point['meeting_key']}")
            except (KeyError, ValueError) as e:
                logger.error(f"Data format error in record: {data_point} → {e}")
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Database error: {e}")

if __name__ == "__main__":
    from database import create_db_and_tables
    create_db_and_tables(populating=True)
