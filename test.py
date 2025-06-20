from urllib.request import urlopen
import json
from db_populate import get_data, URL_BASE

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
"""
##### ---printing---
#print(get_drivers_from_session_key(get_session_key_from_country_year_session_name("Belgium", 2024, "Race")))

"""
DB
TABLE: SESSION_LAPS
DRIVER_ACRONYM,SESSION_KEY,LAP_NUMBER, LAP_TIME, COMPOUND

TABLE: EVENT
LOCATION, YEAR, MEETING_KEY, SESSIONS{session_key, session_type}

TABLE: DRIVERS
PK(ACRONYM+SESSION_KEY), SESSION_KEY, NAME, LAST_NAME, ACRONYM, NUMBER, TEAM, HEADSHOT_URL

TABLE: SESSIONS
LOCATION, SESSION_KEY, SESSION_TYPE, SESSION_NAME, DATE

TABLE: SESSION_RESULT
SESSION_KEY, DRIVER(ACRONYM), FINAL_POSITION
"""
def get_sessions():
    url = URL_BASE + f'sessions?year=2024'
    data = get_data(url)
    for datapoint in data:
        print(datapoint)

def get_drivers():
    url = URL_BASE + 'drivers'
    data = get_data(url)
    for datapoint in data:
        print(datapoint)

def get_laps():
    url = URL_BASE + 'laps'
    data = get_data(url)
    for datapoint in data:
        print(datapoint)
#get_sessions()
#get_drivers()
get_laps()