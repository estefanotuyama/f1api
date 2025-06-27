import sys
from pathlib import Path

from db.db_utils import create_event_entity

sys.path.append(str(Path(__file__).resolve().parent.parent))  # Adds project root to import path


from database import engine
from sqlmodel import Session, select
from models.events import Event
from db_utils import URL_BASE, get_data, logger
from datetime import datetime

YEAR = str(datetime.today().year)
meeting_keys_already_added = set()
new_meeting_keys = []

# smartest way to do this? one would be always loop through meeting keys to add session key.
# other would be to for that meeting, only add it to the 'already added' if the last session was a race
# (problem: then we would always be readding preseason practice) todo: think

# one alternative would be to always use 'latest' key, but that would mean we need to run this every weekend.

def fetch_meeting_keys_already_added():
    with Session(engine) as session:
        events = session.exec(select(Event.meeting_key)).all()
        for event in events:
            pass # need to make a decision on what logic to use here

def add_missing_event_data():
    events_data = get_data(URL_BASE+f'meetings?year={YEAR}')
    with Session(engine) as session:
        for data_point in events_data:
            if not (event['meeting_key'] in meeting_keys_already_added):
                event = create_event_entity(data_point)
                session.add(event)
                session.commit()
                new_meeting_keys.append(event['meeting_key'])
                logger.info(f"Event added: {data_point['meeting_official_name']}")

meeting_keys_already_added.add(set(fetch_meeting_keys_already_added()))
add_missing_event_data()