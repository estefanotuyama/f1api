from backend.models.driver import Driver
from backend.models.session_driver import SessionDriver
from backend.models.events import Event
from backend.db.database import engine
from backend.db.db_utils import URL_BASE, get_data, logger, map_stints_laps, FALLBACK_COMPOUND
from backend.models.session_laps import SessionLaps
from backend.models.session_result import SessionResult
from backend.models.sessions import F1Session
from sqlalchemy import URL, select
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

def add_meetings_to_db(session: Session):
    """
    Queries the Event (meeting) from OpenF1 API and adds it to the database.
    :param session: Database session
    :param meeting_key: Unique meeting identifier
    :return: Boolean informing if the meeting was successfully added
    """
    meetings = get_data(f'{URL_BASE}meetings')


    for meeting in meetings:

        existing = session.get(Event, meeting['meeting_key'])
        if existing:
            logger.info(f"Meeting {str(meeting['meeting_key'])} already exists in DB, skipping.")
            return

        new_meeting = Event(
                    meeting_key=meeting.get('meeting_key'),
                    circuit_key=meeting.get('circuit_key'),
                    location=meeting.get('location'),
                    country_name=meeting.get('country_name'),
                    circuit_name=meeting.get('circuit_short_name'),
                    meeting_official_name=meeting.get('meeting_official_name'),
                    year=meeting.get('year')
                    )

        session.add(new_meeting)
        logger.info(f"Staged meeting {str(meeting['meeting_key'])} for addition.")

def add_session_to_db(session:Session, f1session: dict):
    """
    Adds an F1Session to the database.
    :param session: Database Session
    :param f1session: Formula 1 Session (race, practice, qualifying, etc.)
    :return: None if the session is already in the DB.
    """
    existing = session.get(F1Session, f1session['session_key'])
    if existing:
        logger.info(f"Session {str(f1session['session_key'])} already exists, skipping.")
        return
    new_f1session = F1Session(
        location=f1session.get('location'),
        meeting_key=f1session.get('meeting_key'),
        session_key=f1session.get('session_key'),
        session_type=f1session.get('session_type'),
        session_name=f1session.get('session_name'),
        date=f1session.get('date_start')
    )
    session.add(new_f1session)
    logger.info(f"Staged session {str(f1session['session_key'])} for addition.")

def add_session_drivers_to_db(session:Session, session_key:int):
    """
    Gets all the drivers in an F1 Session from OpenF1 API and adds them to the db. Also call
    the method that adds a driver's laps to the DB `add_drivers_laps_to_db`.
    :param session: Database Session
    :param session_key: Unique F1 Session identifier.
    """
    url = URL_BASE + f"drivers?session_key={str(session_key)}"
    data = get_data(url)
    for driver_data in data:
        # Check if driver exists in Driver table
        driver = session.exec(
            select(Driver).where(
                Driver.first_name == driver_data['first_name'],
                Driver.last_name == driver_data['last_name'],
                Driver.name_acronym == driver_data['name_acronym']
            )
        ).first()

        if not driver:
            new_driver = Driver(
                driver_number=driver_data.get('driver_number'),
                first_name=driver_data.get('first_name'),
                last_name=driver_data.get('last_name'),
                name_acronym=driver_data.get('name_acronym'),
                headshot_url=driver_data.get('headshot_url', "")
            )
            session.add(new_driver)
            session.flush()
            session.refresh(new_driver)
            driver = new_driver
            logger.info(f"Staged driver {driver_data['name_acronym']} for addition.")

        # Check if SessionDriver entry exists
        session_driver = session.get(SessionDriver, (session_key, driver.id))
        if not session_driver:
            new_session_driver = SessionDriver(
                session_key=session_key,
                driver_id=driver.id,
                team=driver_data.get('team_name')
            )
            session.add(new_session_driver)
            logger.info(f"Staged driver {driver_data['name_acronym']} in session {str(session_key)} for addition.")

        #now we add this driver's session laps to the DB
        add_drivers_laps_to_db(session, session_key, driver.id, driver_data['driver_number'])

def add_drivers_laps_to_db(session:Session, session_key:int, driver_id:int, driver_number:int):
    """
    Adds all laps information from a driver in a session.
    :param session: Database session
    :param session_key: Unique F1 session identifier
    :param driver_id: The driver's unique id
    :param driver_number: The driver's number in the session
    """
    laps_url = URL_BASE + f'laps?session_key={str(session_key)}&driver_number={str(driver_number)}'
    lap_data = get_data(laps_url)

    stints_url = URL_BASE + f"stints?session_key={str(session_key)}&driver_number={str(driver_number)}"
    stints_data = get_data(stints_url)
    stints_hashmap = map_stints_laps(stints_data)

    for lap in lap_data:
        existing = session.exec(
            select(SessionLaps).where(
                (SessionLaps.driver_id == driver_id) &
                (SessionLaps.session_key == lap['session_key']) &
                (SessionLaps.lap_number == lap['lap_number'])
            )
        ).first()
        if existing:
            logger.info(f"Lap {lap['lap_number']} already exists, skipping.")
            continue

        compound = stints_hashmap.get(lap['lap_number'], FALLBACK_COMPOUND)

        new_lap = SessionLaps(
            driver_id=driver_id,
            session_key=lap.get('session_key'),
            lap_number=lap.get('lap_number'),
            is_pit_out_lap=lap.get('is_pit_out_lap'),
            lap_time=lap.get('lap_duration', 0.0),
            st_speed=lap.get('st_speed', 0),
            compound=compound
        )
        session.add(new_lap)
        logger.info(f"Staged lap {lap['lap_number']} of driver {driver_number} in session {str(session_key)} for addition.")

def add_session_result_to_db(session:Session, session_key:int):
    """
    Queries OpenF1 API for session results and adds it to db.
    :param session: Database session.
    :param session_key: Unique F1 session key identifier
    :return: returns early if exception.
    """
    data = get_data(URL_BASE + f'session_result?session_key={session_key}')
    for datapoint in data:
            driver = session.exec(
                select(Driver).where(Driver.driver_number == datapoint['driver_number'])
            ).first()
            if not driver:
                logger.error(f"Driver with number {datapoint['driver_number']} not found in Driver table.")
                continue

            existing = session.exec(
                select(SessionResult).where(
                    (SessionResult.driver_id == driver.id) &
                    (SessionResult.session_key == datapoint['session_key'])
                )
            ).first()
            if existing:
                logger.info(f"Session result for driver {str(datapoint['driver_number'])} in session {str(session_key)} already exists, skipping.")
                continue
            sr_entry = SessionResult(
                meeting_key=datapoint.get('meeting_key'),
                session_key=datapoint.get('session_key'),
                driver_id=driver.id,
                position=datapoint.get('position'),
                duration=str(datapoint.get('duration')),
                number_of_laps=datapoint.get('number_of_laps'),
                gap_to_leader=str(datapoint.get('gap_to_leader')),
                dnf=datapoint.get('dnf'),
                dns=datapoint.get('dns'),
                dsq=datapoint.get('dsq')
            )
            session.add(sr_entry)
    logger.info(f"Staged session results of session {str(session_key)} for addition.")

def update_db():
    """
    Controls the flow to update the database, calling all necessary methods.
    """
    with Session(engine) as session:
        latest_session_date = fetch_latest_session(session)

        if latest_session_date:
            url = URL_BASE + f'sessions?date_start>{latest_session_date}'
        # if this is the first time populating the script (no latest session in db), get all sessions
        else:
            url = URL_BASE + f'sessions'
        data = get_data(url)

        try:
            add_meetings_to_db(session)
            session.commit()
        except Exception as e:
            logger.error(f"Failed to add meetings to db. Error: {e}")

        for f1session in data:
            try:
                with session.begin():
                    add_session_to_db(session, f1session)
                    add_session_result_to_db(session, f1session['session_key'])
                    # the method below also adds the driver's laps to the DB
                    add_session_drivers_to_db(session, f1session['session_key'])
                logger.info(f"Comitted all info for session {str(f1session['session_key'])}")
            except Exception:
                logger.error(
                    f"Transaction failed for session {str(f1session['session_key'])}",
                    exc_info=True,
                )
                break

if __name__ == "__main__":
    from .database import create_db_and_tables
    create_db_and_tables(populating=True)
