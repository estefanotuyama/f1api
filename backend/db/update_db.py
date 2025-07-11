from backend.models.drivers import Driver
from backend.models.events import Event
from backend.db.database import engine
from backend.db.db_utils import URL_BASE, get_data, logger, add_session_tire_compound_info
from backend.models.session_laps import SessionLaps
from backend.models.sessions import F1Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlmodel import Session, select, desc

"""
This is the script that updates the database.
"""

def fetch_latest_session(session: Session) -> str:
    """
    Queries the database to find the latest session we have a record of.
    :param session: Database session
    :return: Latest 'F1Session' session
    """
    result = session.exec(
        select(F1Session.date).order_by(desc(F1Session.date))
    ).first()
    return result

def fetch_meeting_keys(session:Session) -> set:
    """
    Queries database to fetch all meeting keys available.
    :param session: Database Session
    :return: Set of meeting keys
    """
    results = session.exec(select(Event.meeting_key)).all()
    return set(results)

#returns true if successfuly added meeting key to db
def add_meeting_to_db(session: Session, meeting_key:int):
    """
    Queries the Event (meeting) from OpenF1 API and adds it to the database.
    :param session: Database session
    :param meeting_key: Unique meeting identifier
    :return: Boolean informing if the meeting was successfully added
    """
    try:
        meeting_data = get_data(URL_BASE + f'meetings?meeting_key={str(meeting_key)}')[0]
        single_meeting_data = meeting_data[0]
        new_meeting = Event(
                    meeting_key=single_meeting_data['meeting_key'],
                    circuit_key=single_meeting_data['circuit_key'],
                    location=single_meeting_data['location'],
                    country_name=single_meeting_data['country_name'],
                    circuit_name=single_meeting_data['circuit_short_name'],
                    meeting_official_name=single_meeting_data['meeting_official_name'],
                    year=single_meeting_data['year']
                    )
        existing = session.get(Event, single_meeting_data["meeting_key"])
        if existing:
            return False
        session.add(new_meeting)
        session.commit()
        return True
    except (IntegrityError, KeyError, ValueError, SQLAlchemyError):
        session.rollback()
        logger.error("Failure to add event")
        return False

def add_session_to_db(session:Session, f1session: dict):
    """
    Adds an F1Session to the database.
    :param session: Database Session
    :param f1session: Formula 1 Session (race, practice, qualifying etc.)
    :return: None if the session is already in the DB.
    """
    try:
        existing = session.get(F1Session, f1session['session_key'])
        if existing:
            return None
        new_f1session = F1Session(
            location=f1session['location'],
            meeting_key=f1session['meeting_key'],
            session_key=f1session['session_key'],
            session_type=f1session['session_type'],
            session_name=f1session['session_name'],
            date=f1session['date_start']
        )
        session.add(new_f1session)
        session.commit()
        logger.info("Session added successfully")
    except (IntegrityError, KeyError, ValueError, SQLAlchemyError) as e:
        session.rollback()
        raise e("Error while adding session to DB")


def add_session_drivers_to_db(session:Session, session_key:int):
    """
    Gets all the drivers in an F1 Session from OpenF1 API and adds them to the db. Also call
    the method that adds a driver's laps to the DB `add_drivers_laps_to_db`.
    :param session: Database Session
    :param session_key: Unique F1 Session identifier.
    """
    try:
        url = URL_BASE + f"drivers?session_key={str(session_key)}"
        data = get_data(url)
        for driver in data:
            existing = session.get(Driver, (driver['name_acronym'], driver['session_key']))
            if existing:
                add_drivers_laps_to_db(session, driver['session_key'], driver['driver_number'])
                continue
            new_driver = Driver(
                    session_key=driver['session_key'],
                    first_name=driver['first_name'],
                    last_name=driver['last_name'],
                    name_acronym=driver['name_acronym'],
                    number=driver['driver_number'],
                    team=driver['team_name'],
                    headshot_url=driver['headshot_url'] or ""
                )
            session.add(new_driver)
            session.commit()
            #now we add this driver's laps to the DB so its more efficient
            add_drivers_laps_to_db(session, driver['session_key'], driver['driver_number'])

    except (IntegrityError, KeyError, ValueError, SQLAlchemyError) as e:
        session.rollback()
        raise e("Error while adding driver laps to DB")

def add_drivers_laps_to_db(session:Session, session_key:int, driver_number:int):
    """
    Adds all laps information from a driver in a session.
    :param session: Database session
    :param session_key: Unique F1 session identifier
    :param driver_number: F1 driver's number
    """
    url = URL_BASE + f'laps?session_key={str(session_key)}&driver_number={str(driver_number)}'
    data = get_data(url)

    for lap in data:
        existing = session.exec(
            select(SessionLaps).where(
                SessionLaps.driver_number == lap['driver_number'],
                SessionLaps.session_key == lap['session_key'],
                SessionLaps.lap_number == lap['lap_number']
            )
        ).first()
        if existing:
            logger.info("Lap already exists, skipping.")
            continue
        try:
            new_lap = SessionLaps(
                driver_number=lap['driver_number'],
                session_key=lap['session_key'],
                lap_number=lap['lap_number'],
                is_pit_out_lap=lap['is_pit_out_lap'],
                lap_time=lap['lap_duration'] or 0.0,
                st_speed=lap['st_speed'] or 0
            )
            session.add(new_lap)
            session.commit()
        except (IntegrityError, KeyError, ValueError, SQLAlchemyError) as e:
            session.rollback()
            continue

def update_db():
    """
    Controls the flow to update the database, calling all necessary methods.
    """
    with Session(engine) as session:
        latest_session_date = fetch_latest_session(session)

        url = URL_BASE + f'sessions?date_start>{latest_session_date}'
        data = get_data(url)

        meeting_keys = fetch_meeting_keys(session)
        for f1session in data:
            if not (f1session['meeting_key'] in meeting_keys):
                added = add_meeting_to_db(session, f1session['meeting_key'])
                if added:
                    meeting_keys.add(f1session['meeting_key'])
            try:
                add_session_to_db(session, f1session)
                # the method below also adds the driver's laps to the DB
                add_session_drivers_to_db(session, f1session['session_key'])
                add_session_tire_compound_info(session, f1session['session_key'])
                logger.info(f"Added all info for session {str(f1session['session_key'])}")
            except (IntegrityError, KeyError, ValueError, SQLAlchemyError) as e:
                session.rollback()
                logger.error(e)

update_db()