from backend.models.drivers import Driver
from backend.models.events import Event
from backend.db.database import engine
from backend.db.db_utils import URL_BASE, get_data, logger, map_stints_laps, FALLBACK_COMPOUND
from backend.models.session_laps import SessionLaps
from backend.models.session_result import SessionResult
from backend.models.sessions import F1Session
from sqlalchemy import select
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

def add_meeting_to_db(session: Session, meeting_key:int):
    """
    Queries the Event (meeting) from OpenF1 API and adds it to the database.
    :param session: Database session
    :param meeting_key: Unique meeting identifier
    :return: Boolean informing if the meeting was successfully added
    """
    existing = session.get(Event, meeting_key)
    if existing:
        logger.info(f"Meeting {str(meeting_key)} already exists in DB, skipping.")
        return

    meeting_data = get_data(URL_BASE + f'meetings?meeting_key={str(meeting_key)}')[0]

    new_meeting = Event(
                meeting_key=meeting_data.get('meeting_key'),
                circuit_key=meeting_data.get('circuit_key'),
                location=meeting_data.get('location'),
                country_name=meeting_data.get('country_name'),
                circuit_name=meeting_data.get('circuit_short_name'),
                meeting_official_name=meeting_data.get('meeting_official_name'),
                year=meeting_data.get('year')
                )

    session.add(new_meeting)
    logger.info(f"Staged meeting {str(meeting_data['meeting_key'])} for addition.")

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
    for driver in data:
        existing = session.get(Driver, (driver['name_acronym'], driver['session_key']))
        if existing:
            logger.info(f"Driver {driver['name_acronym']} already exists in session {str(session_key)}, staging session laps now.")
            add_drivers_laps_to_db(session, driver['session_key'], driver['driver_number'])
            continue
        new_driver = Driver(
                session_key=driver.get('session_key'),
                first_name=driver.get('first_name'),
                last_name=driver.get('last_name'),
                name_acronym=driver.get('name_acronym'),
                number=driver.get('driver_number'),
                team=driver.get('team_name'),
                headshot_url=driver.get('headshot_url', "")
            )
        session.add(new_driver)
        #now we add this driver's session laps to the DB
        add_drivers_laps_to_db(session, driver['session_key'], driver['driver_number'])
        logger.info(f"Staged driver {driver['name_acronym']} in session {str(session_key)} for addition.")

def add_drivers_laps_to_db(session:Session, session_key:int, driver_number:int):
    """
    Adds all laps information from a driver in a session.
    :param session: Database session
    :param session_key: Unique F1 session identifier
    :param driver_number: F1 driver's number
    """
    laps_url = URL_BASE + f'laps?session_key={str(session_key)}&driver_number={str(driver_number)}'
    lap_data = get_data(laps_url)

    stints_url = URL_BASE + f"stints?session_key={str(session_key)}&driver_number={str(driver_number)}"
    stints_data = get_data(stints_url)
    stints_hashmap = map_stints_laps(stints_data)

    for lap in lap_data:
        existing = session.exec(
            select(SessionLaps).where(
                (SessionLaps.driver_number == lap['driver_number']) &
                (SessionLaps.session_key == lap['session_key']) &
                (SessionLaps.lap_number == lap['lap_number'])
            )
        ).first()
        if existing:
            logger.info(f"Lap {lap['lap_number']} already exists, skipping.")
            continue

        compound = stints_hashmap.get(lap['lap_number'], FALLBACK_COMPOUND)

        new_lap = SessionLaps(
            driver_number=lap.get('driver_number'),
            session_key=lap.get('session_key'),
            lap_number=lap.get('lap_number'),
            is_pit_out_lap=lap.get('is_pit_out_lap'),
            lap_time=lap.get('lap_duration', 0.0),
            st_speed=lap.get('st_speed', 0),
            compound=compound
        )
        session.add(new_lap)
        logger.info(f"Staged lap {lap['lap_number']} of driver {lap['driver_number']} in session {str(session_key)} for addition.")

def add_session_result_to_db(session:Session, session_key:int):
    """
    Queries OpenF1 API for session results and adds it to db.
    :param session: Database session.
    :param session_key: Unique F1 session key identifier
    :return: returns early if exception.
    """
    data = get_data(URL_BASE + f'session_result?session_key={session_key}')
    for datapoint in data:
            existing = session.exec(
                select(SessionResult).where(
                    (SessionResult.driver_number == datapoint['driver_number']) &
                    (SessionResult.session_key == datapoint['session_key'])
                )
            ).first()
            if existing:
                logger.info(f"Session result for driver {str(datapoint['driver_number'])} in session {str(session_key)} already exists, skipping.")
                continue
            sr_entry = SessionResult(
                meeting_key=datapoint.get('meeting_key'),
                session_key=datapoint.get('session_key'),
                driver_number=datapoint.get('driver_number'),
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

        meeting_keys = fetch_meeting_keys(session)
        for f1session in data:
            try:
                with session.begin():
                    if f1session['meeting_key'] not in meeting_keys:
                        add_meeting_to_db(session, f1session['meeting_key'])
                        meeting_keys.add(f1session['meeting_key'])

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

if __name__ == "__main__":
    from database import create_db_and_tables
    create_db_and_tables(populating=True)