from sqlalchemy.orm import exc
from backend.models.driver import Driver
from backend.models.session_driver import SessionDriver
from backend.models.events import Event
from backend.db.database import engine
from backend.db.db_utils import URL_BASE, get_data, logger, map_stints_laps, FALLBACK_COMPOUND
from backend.models.session_laps import SessionLaps
from backend.models.session_result import SessionResult
from backend.models.sessions import F1Session
from sqlalchemy import select
from sqlmodel import Session, distinct, select, desc
from collections import defaultdict

from backend.models.teams import Teams

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

def add_drivers_and_session_links(session: Session, session_key: int, all_drivers_data: list[dict]):
    """
    Adds drivers to the DB if they don't exist and links them to the session.
    This function NO LONGER fetches data, it just processes a list of driver data.
    """
    for driver_data in all_drivers_data:
        acronym = driver_data.get('name_acronym')
        if not acronym:
            continue

        driver = session.exec(
            select(Driver).where(Driver.name_acronym == acronym)
        ).first()

        if driver:
            made_update = False
            new_first_name = driver_data.get('first_name')
            new_last_name = driver_data.get('last_name')
            new_headshot_url = driver_data.get('headshot_url')

            if driver.first_name == "" and new_first_name:
                driver.first_name = new_first_name
                made_update = True

            if driver.last_name == "" and new_last_name:
                driver.last_name = new_last_name
                made_update = True

            if driver.headshot_url == "" and new_headshot_url:
                driver.headshot_url = new_headshot_url
                made_update = True

            if made_update:
                session.add(driver)
                logger.info(f"Updated missing name for driver {acronym}.")

        else:
            driver = Driver(
                first_name=driver_data.get('first_name', ""),
                last_name=driver_data.get('last_name', ""),
                name_acronym=acronym,
                headshot_url=driver_data.get('headshot_url', "")
            )
            session.add(driver)
            session.flush()
            session.refresh(driver)
            logger.info(f"Staged new driver {acronym} for addition (with placeholders if needed).")
        # save driver id for later
        driver_data['driver_id'] = driver.id

        session_driver = session.get(SessionDriver, (session_key, driver.id))
        if not session_driver:
            new_session_driver = SessionDriver(
                session_key=session_key,
                driver_id=driver.id,
                team=driver_data.get('team_name'),
                driver_number=driver_data.get('driver_number')
            )
            session.add(new_session_driver)
            logger.info(f"Staged driver {driver_data['name_acronym']} in session {str(session_key)} for addition.")

def add_all_laps_for_session(session: Session, session_key: int):
    """
    Efficiently fetches and adds all laps for all drivers in a session.
    """
    logger.info(f"Starting bulk lap/stint processing for session {session_key}.")

    # bulk fetch all lap and stint data for a session
    laps_url = URL_BASE + f'laps?session_key={str(session_key)}'
    all_laps_data = get_data(laps_url)

    stints_url = URL_BASE + f"stints?session_key={str(session_key)}"
    all_stints_data = get_data(stints_url)

    # group data for ease of access
    laps_by_driver = defaultdict(list)
    for lap in all_laps_data:
        laps_by_driver[lap['driver_number']].append(lap)

    stints_by_driver = defaultdict(list)
    for stint in all_stints_data:
        stints_by_driver[stint['driver_number']].append(stint)

    drivers_url = URL_BASE + f"drivers?session_key={str(session_key)}"
    all_drivers_data = get_data(drivers_url)

    # ensure all drivers and their session links are in the DB
    add_drivers_and_session_links(session, session_key, all_drivers_data)

    for driver_data in all_drivers_data:
        driver_number = driver_data['driver_number']
        driver_id = driver_data['driver_id']

        # get laps and stints for this driver from our in-memory groups
        driver_laps = laps_by_driver.get(driver_number, [])
        driver_stints = stints_by_driver.get(driver_number, [])

        if not driver_laps:
            continue 

        stints_hashmap = map_stints_laps(driver_stints)

        for lap in driver_laps:
            existing = session.exec(
                select(SessionLaps).where(
                    (SessionLaps.driver_id == driver_id) &
                    (SessionLaps.session_key == lap['session_key']) &
                    (SessionLaps.lap_number == lap['lap_number'])
                )
            ).first()
            if existing:
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
    logger.info(f"Staged all laps for session {session_key}.")

def add_session_result_to_db(session:Session, session_key:int):
    """
    Queries OpenF1 API for session results and adds it to db.
    :param session: Database session.
    :param session_key: Unique F1 session key identifier
    :return: returns early if exception.
    """
    data = get_data(URL_BASE + f'session_result?session_key={session_key}')
    for datapoint in data:
        session_driver_link = session.exec(
            select(SessionDriver).where(
                SessionDriver.session_key == session_key,
                SessionDriver.driver_number == datapoint.get('driver_number')
            )
        ).first()

        if not session_driver_link:
            logger.error(f"Could not find a SessionDriver link for driver number "
                         f"{datapoint.get('driver_number')} in session {session_key}. Skipping result.")
            continue

        driver_id = session_driver_link.driver_id

        existing = session.exec(
            select(SessionResult).where(
                (SessionResult.driver_id == driver_id) &
                (SessionResult.session_key == datapoint['session_key'])
            )
        ).first()

        if existing:
            logger.info(f"Session result for driver {str(datapoint['driver_number'])} in session {str(session_key)} already exists, skipping.")
            continue

        sr_entry = SessionResult(
            meeting_key=datapoint.get('meeting_key'),
            session_key=datapoint.get('session_key'),
            driver_id=driver_id,
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

def add_teams_colors(session:Session):
    try: 
        teams = session.exec(select(distinct(SessionDriver.team)))

        for team in teams:
            if not team:
                continue
            team_fmt = team.replace(' ', '%20')
            data = get_data(URL_BASE + f'drivers?team_name={team_fmt}')[0]
            if not data :
                continue
            team_colour = data.get('team_colour')

            team = Teams(
                name=team,
                color=f'#{team_colour}'
            )
            session.add(team)
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Error while adding teams to the DB: {e}")

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

        data_size = len(data)
        c= 0
        for f1session in data:
            try:
                with session.begin():
                    session_key = f1session['session_key']
                    add_session_to_db(session, f1session)
                    add_all_laps_for_session(session, session_key)
                    add_session_result_to_db(session, session_key)
                c += 1
                logger.info(f"Committed all info for session {str(session_key)}. Progress: ({c}/{data_size})")
            except Exception:
                logger.error(
                    f"Transaction failed for session {str(f1session['session_key'])}",
                    exc_info=True,
                )
                break
        add_teams_colors(session)

if __name__ == "__main__":
    from .database import create_db_and_tables
    create_db_and_tables(populating=True)
