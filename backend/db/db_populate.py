from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlmodel import Session
from database import engine
from db_utils import get_session_keys, get_session_laps, logger, URL_BASE, get_data
from backend.models.drivers import Driver
from backend.models.events import Event
from backend.models.sessions import F1Session
from backend.models.session_laps import SessionLaps

"""
This script is responsible for populating the database from the ground up. Populates
everthing, from f1 events to sessions to session laps.
Takes a while to run.
"""

YEARS = [2023, 2024, 2025]

def populate_db():
    """
    Handles database populating, calling methods that populate each table.
    """
    #populate events
    add_events_data()
    logger.info("Events added successfully!")
    #populate sessions
    add_sessions_data()
    logger.info("Sessions added successfully!")
    #populate drivers
    add_drivers_data()
    logger.info("Drivers added successfully!")
    #populate laps times
    add_laps_data()
    logger.info("Laps data added successfully!")

# EVENTS POPULATE(2024)
def add_events_data():
    """
    Adds all events data to the database. An F1 event is the entire race weekend,
    or testing session (the one at the start of an F1 season).
    Request the data from the OpenF1 AP1, create the Model and upload to the Event table.
    """
    for year in YEARS:
        events_data = get_data(URL_BASE + f'meetings?year={year}')
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

# SESSIONS POPULATE
def add_sessions_data():
    """
    Adds all F1 sessions to the database. An F1 session can be a Free Practice 1, 2 or 3,
    Qualifying or Race (Sprints included).
    Request data for all sessions in a year from the OpenF1 API, create the Model and
    add the session to the F1Session table.
    """
    for year in YEARS:
        url = URL_BASE + f'sessions?year={year}'
        data = get_data(url)
        with Session(engine) as session:
            for data_point in data:
                try:
                    f1session = F1Session(
                        location=data_point['location'],
                        meeting_key=data_point['meeting_key'],
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
    """
    Adds all drivers to the database. There are a lot of entries to this table, since we have
    the same driver but with different session keys for ease of access. This can and should
    be changed later for optimization purposes.
    Request data from OpenF1 API, create the Model and add it to the Driver database.
    """
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
#todo: review how we can optimize this, as this is the part that takes the longest to run.
def add_laps_data():
    """
    Adds all driver laps to the database. There are a LOT of laps in a session, and a lot
    of sessions. This is the part that takes the longest to run. We still need to
    incorporate the code that fetches the compound used for each lap, since OpenF1 API
    does not provide that.
    Request the session data from OpenF1 API -> for each datapoint, extract the lap data
    and add it to the database.
    """
    with Session(engine) as session:
        session_keys = get_session_keys()
        for session_key in session_keys:
            data = get_session_laps(session_key)
            for datapoint in data:
                # Check if the record already exists
                existing = session.exec(
                    select(SessionLaps).where(
                        SessionLaps.driver_number == datapoint['driver_number'],
                        SessionLaps.session_key == datapoint['session_key'],
                        SessionLaps.lap_number == datapoint['lap_number']
                    )
                ).first()
                if existing:
                    logger.info("Lap already exists, skipping.")
                    continue
                try:
                    lap_info = SessionLaps(
                        driver_number=datapoint['driver_number'],
                        session_key=datapoint['session_key'],
                        lap_number=datapoint['lap_number'],
                        is_pit_out_lap=datapoint['is_pit_out_lap'],
                        lap_time=datapoint['lap_duration'] or 0.0,
                        st_speed=datapoint['st_speed'] or 0
                    )
                    print(datapoint['lap_duration'])
                    session.add(lap_info)
                    session.commit()
                    logger.info(f"Lap added! Current session key: {str(datapoint['session_key'])}")
                except IntegrityError as e:
                    session.rollback()
                    logger.error(f"IntegrityError: {e.orig}")
                except SQLAlchemyError as e:
                    session.rollback()
                    logger.error(f"Database error: {e}")

if __name__ == "__main__":
    from database import create_db_and_tables
    create_db_and_tables(populating=True)