import logging, time, json
from typing import Annotated
from urllib.error import HTTPError, URLError
from urllib.request import urlopen
from fastapi import Depends
from sqlalchemy import select, distinct
from sqlmodel import Session
from backend.db.database import engine, get_session
from backend.models.drivers import Driver

"""This script has utilities we use to assist database operations."""

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

SessionDep = Annotated[Session, Depends(get_session)]
URL_BASE = "https://api.openf1.org/v1/"
FALLBACK_COMPOUND = "Not provided"

def get_data(url: str, retries: int = 5, backoff: float = 1.0):
    """
    Fetches data from the OpenF1 API given a request URL.
    OpenF1 API is unstable, so we have a retrying logic in case something fails.
    :param url: URL for which we want to request data.
    :param retries: Number of retries if request fails.
    :param backoff: Time to wait if failure.
    :return: Data requested, a list of dictionaries.
    """
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

def get_session_keys():
    """
    Fetches all session keys available in the database.
    :return: Data requested, a list of session keys.
    """
    with Session(engine) as session:
        query = select(distinct(Driver.session_key))
        result = session.execute(query).scalars().all()
        return result

def get_session_laps(session_key):
    """
    Requests all laps in a given session from the OpenF1 API
    :param session_key: Unique F1 session identifier.
    :return: Data requested, a list of dictionaries.
    """
    url = URL_BASE + f'laps?session_key={session_key}'
    data = get_data(url)
    return data

def map_stints_laps(stints:dict):
    """
    Maps a lap number to the compound used in a stint.
    :param stints: Dictionary containing stint data.
    :return: Dictionary containing the mapping.
    """
    stints_hashmap = {}
    for stint in stints:
        try:
            for i in range(stint['lap_start'], stint['lap_end'] + 1):
                stints_hashmap[i] = stint['compound'] or FALLBACK_COMPOUND
        except TypeError:
            logger.info(f"Unkown stint data for driver {stint['driver_number']} on session {stint['session_key']}")
            return {i: FALLBACK_COMPOUND for i in range(1, 80)}
    return stints_hashmap
