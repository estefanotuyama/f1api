from typing import Annotated
from urllib.request import urlopen
import json

from fastapi import Depends
from sqlalchemy import select, distinct
from sqlmodel import Session

from db.database import engine, get_session
from models.drivers import Driver

SessionDep = Annotated[Session, Depends(get_session)]
URL_BASE = "https://api.openf1.org/v1/"

def get_data(url):
    response = urlopen(url)
    data=json.loads(response.read().decode('utf-8'))
    return data

def get_sessions():
    url = URL_BASE + f'sessions?session_key=9956'
    data = get_data(url)
    for datapoint in data:
        print(datapoint)

def get_drivers():
    url = URL_BASE + 'drivers'
    data = get_data(url)
    for datapoint in data:
        print(datapoint)

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
