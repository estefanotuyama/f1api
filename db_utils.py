from urllib.request import urlopen
import json

from sqlalchemy import select, distinct
from sqlmodel import Session

from database import engine
from models.drivers import Driver

"""response = urlopen('https://api.openf1.org/v1/laps?session_key=9161&driver_number=63')
data = json.loads(response.read().decode('utf-8'))

def get_response(search_url):
    response = urlopen(search_url)
    data = json.loads(response.read().decode('utf-8'))
    return data

def get_session_key_from_country_year_session_name(country, year, session_name):
    search_url = BASE_URL + f'sessions?country_name={country}&session_name={session_name}&year={year}'
    data = get_response(search_url)
    return data[0]['session_key']

def get_drivers_from_session_key(session_key):
    search_url = BASE_URL + f'drivers?session_key={session_key}'
    data = get_response(search_url)
    return data
DB
TABLE: SESSION_LAPS
DRIVER_NUM,SESSION_KEY,LAP_NUMBER, LAP_TIME, ST_SPEED, COMPOUND

TABLE: EVENT
LOCATION, YEAR, MEETING_KEY, SESSIONS{session_key, session_type}

TABLE: DRIVERS
PK(ACRONYM+SESSION_KEY), SESSION_KEY, NAME, LAST_NAME, ACRONYM, NUMBER, TEAM, HEADSHOT_URL

TABLE: SESSIONS
LOCATION, SESSION_KEY, SESSION_TYPE, SESSION_NAME, DATE

TABLE: SESSION_RESULT
SESSION_KEY, DRIVER(ACRONYM), FINAL_POSITION
"""
URL_BASE = "https://api.openf1.org/v1/"
def get_data(url):
    response = urlopen(url)
    data=json.loads(response.read().decode('utf-8'))
    return data

def get_sessions():
    url = URL_BASE + f'sessions?year=2025'
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

"""data = get_laps(10033)
for datapoint in data:
    print(datapoint)"""