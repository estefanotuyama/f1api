import logging
from typing import Annotated
from urllib.request import urlopen
import json

from fastapi import Depends
from sqlalchemy import select, distinct
from sqlmodel import Session

from db.database import engine, get_session
from db.update_db import fetch_latest_session
from models.drivers import Driver
from models.events import Event

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

def get_sessions(meeting_key:int):
    url = URL_BASE + f'sessions?session_key={meeting_key}'
    data = get_data(url)
    return data

def get_drivers():
    url = URL_BASE + 'drivers'
    data = get_data(url)
    return data


def get_session_keys():
    with Session(engine) as session:
        stmt = select(distinct(Driver.session_key))
        result = session.execute(stmt).scalars().all()
        return result

def get_laps(session_key):
    url = URL_BASE + f'laps?session_key={session_key}'
    data = get_data(url)
    return data

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
