import logging
import time
from typing import Annotated
from urllib.error import HTTPError, URLError
from urllib.request import urlopen
import json

from fastapi import Depends
from sqlalchemy import select, distinct
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlmodel import Session

from backend.db.database import engine, get_session
from backend.models.drivers import Driver
from backend.models.events import Event
from backend.models.session_laps import SessionLaps
from backend.models.sessions import F1Session

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

SessionDep = Annotated[Session, Depends(get_session)]
URL_BASE = "https://api.openf1.org/v1/"

def get_data(url):
    response = urlopen(url)
    data=json.loads(response.read().decode('utf-8'))
    return data

def get_data(url: str, retries: int = 5, backoff: float = 1.0):
    for attempt in range(retries):
        try:
            with urlopen(url) as response:
                return json.loads(response.read().decode("utf-8"))

        except HTTPError as e:
            if e.code == 429:
                wait_time = 15 * (attempt + 1)
                logger.warning(f"HTTP 429 Too Many Requests: Waiting {wait_time}s before retrying ({attempt+1}/{retries}) → {url}")
                time.sleep(wait_time)
            elif 500 <= e.code < 600:
                logger.warning(f"[Retry {attempt+1}/{retries}] HTTP {e.code}: {url}")
                time.sleep(backoff * (attempt + 1))
            else:
                logger.error(f"Non-retryable HTTPError {e.code} on {url}")
                raise

        except URLError as e:
            logger.warning(f"[Retry {attempt+1}/{retries}] URLError: {e.reason} → {url}")
            time.sleep(backoff * (attempt + 1))

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise

    logger.error(f"❌ Failed after {retries} retries: {url}")
    return None

def get_sessions(meeting_key:int):
    url = URL_BASE + f'sessions?session_key={meeting_key}'
    data = get_data(url)
    return data

def get_drivers():
    url = URL_BASE + 'drivers'
    data = get_data(url)
    return data

def get_session_drivers_number(session:Session, session_key: int):
    return session.exec(select(Driver.number).where(
        Driver.session_key == session_key
    )).all()


def get_session_keys():
    with Session(engine) as session:
        stmt = select(distinct(Driver.session_key))
        result = session.execute(stmt).scalars().all()
        return result

def get_session_laps(session_key):
    url = URL_BASE + f'laps?session_key={session_key}'
    data = get_data(url)
    return data

def get_driver_session_laps(session_key:int, driver_number:int):
    url = URL_BASE + f"laps?session_key={str(session_key)}&driver_number={str(driver_number)}"
    data = get_data(url)
    return data

def get_driver_laps_with_null_compound(session:Session, session_key:int, driver_number:int):
    return session.exec(select(SessionLaps).where(
            (SessionLaps.session_key == session_key) &
            (SessionLaps.driver_number == driver_number) &
            (SessionLaps.compound.is_(None))
        )
    ).scalars().all()

def get_position_from_session_key(session_key):
    url = URL_BASE + f'position?session_key={session_key}'
    data = get_data(url)
    for datapoint in data:
        print(datapoint)

def create_event_entity(data_point: dict):
    event = Event(
        meeting_key=data_point['meeting_key'],
        circuit_key=data_point['circuit_key'],
        location=data_point['location'],
        country_name=data_point['country_name'],
        circuit_name=data_point['circuit_short_name'],
        meeting_official_name=data_point['meeting_official_name'],
        year=data_point['year']
    )
    return event

def map_stints_laps(stints:dict):
    stints_hashmap = {}
    for stint in stints:
        try:
            for i in range(stint['lap_start'], stint['lap_end'] + 1):
                stints_hashmap[i] = stint['compound'] or "Not provided"
        except TypeError:
            logger.info(f"Unkown stint data for driver {stint['driver_number']} on session {stint['session_key']}")
            return {i: "Not provided" for i in range(1, 80)}
    return stints_hashmap

def add_session_tire_compound_info(session:Session, session_key:int):
    """
    OpenF1 doesn't have tire compound data in their laps endpoint,
    so we need to derive it from their 'stints' endpoint
    - **session**: The DB session
    - **session_key**: The session key, so we can fetch that session's data
    """
    #drivers = get_session_drivers(session_key)
    drivers = get_session_drivers_number(session, session_key)
    for driver in drivers:
        # get this driver's laps for this session; driver[0] is the driver number
        laps = get_driver_laps_with_null_compound(session, session_key, driver[0])

        # if there are no laps, means all the tires have compound info
        if len(laps) == 0:
            continue

        # get stints data
        stints_url = URL_BASE + f"stints?session_key={str(session_key)}&driver_number={str(driver[0])}"
        stints = get_data(stints_url)
        stints_hashmap = map_stints_laps(stints)

        # iterate through laps and add tire compound info from hashmap
        for lap in laps:
            try:
                compound = stints_hashmap[lap.lap_number]
                # next:get the lap and update its compound
                lap.compound = compound
                session.add(lap)
            except (IntegrityError, ValueError, SQLAlchemyError, AttributeError) as e:
                session.rollback()
                logger.error(
                    f"Error while adding compound for entity: |{lap.driver_number}|{lap.session_key}|{lap.lap_number}|: {e}"
                )
                continue
            except KeyError:
                # This error may occur for the last lap of a session because of inconsistencies with OpenF1 API.
                lap.compound = "Not provided"
                session.add(lap)
        session.commit()

def add_all_sessions_compound():
    with Session(engine) as session:
        session_keys = session.exec(select(F1Session.session_key)).all()
        for session_key in session_keys:
            try:
                add_session_tire_compound_info(session, session_key[0])
            except (IntegrityError, KeyError, ValueError, SQLAlchemyError) as e:
                logger.error(f"Ran into an error while running 'add_all_sessions_compound' for session {str(session_key)}: {e}")

add_all_sessions_compound()