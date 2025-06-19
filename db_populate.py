from urllib.request import urlopen
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlmodel import Session
from database import engine
from models.drivers import Driver
from models.events import Event
from models.sessions import F1Session
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
    #populate sessions
    add_sessions_data()
    logger.info("Sessions added successfully!")
    #populate drivers
    add_drivers_data()
    logger.info("Drivers added successfully!")

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

# SESSIONS POPULATE(2024)
def add_sessions_data():
    url = URL_BASE + f'sessions?year=2024'
    data = get_data(url)
    with Session(engine) as session:
        for data_point in data:
            try:
                f1session = F1Session(
                    location=data_point['location'],
                    session_key=data_point['session_key'],
                    session_type=data_point['session_type'],
                    session_name=data_point['session_name'],
                    date=data_point['date_start']
                )
                existing = session.get(F1Session, data_point['session_key'])
                if existing:
                    continue
                session.add(f1session)
                session.commit()
                logger.info("Session added successfully ")
            except IntegrityError:
                session.rollback()
                logger.error(f"Duplicate or constraint error for session_key={data_point['meeting_key']}")
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Database error: {e}")

#DRIVERS POPULATE(ALL)
def add_drivers_data():
    url = URL_BASE + 'drivers'
    data = get_data(url)
    with Session(engine ) as session:
        for data_point in data:
            try:
                driver = Driver(
                    session_key=data_point['session_key'],
                    first_name=data_point['first_name'],
                    last_name=data_point['last_name'],
                    name_acronym=data_point['name_acronym'],
                    number=data_point['driver_number'],
                    team=data_point['team_name'],
                    headshot_url=data_point['headshot_url']
                )
                existing = session.get(Driver, (data_point['name_acronym'], data_point['session_key']))
                if existing:
                    continue
                session.add(driver)
                session.commit()
                logger.info(f"Driver with PK {data_point['name_acronym']+str(data_point['session_key'])} added successfully" )
            except IntegrityError:
                session.rollback()
                logger.error(f"Duplicate or constraint error for PK={data_point['name_acronym']+str(data_point['session_key'])}")
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Database error: {e}")

#SESSION LAPS POPULATE(2024):


if __name__ == "__main__":
    from database import create_db_and_tables
    create_db_and_tables(populating=True)
