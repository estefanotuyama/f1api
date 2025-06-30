import sys
from pathlib import Path

from models.events import Event

sys.path.append(str(Path(__file__).resolve().parent.parent))  # Adds project root to import path

from db.database import get_session, engine
from db.db_utils import URL_BASE, get_data
from models.sessions import F1Session
from sqlmodel import Session, select, desc

## THIS IS HOW WE DO IT! WAY EASIER! fetch latest session> boom
#url = URL_BASE + f'sessions?date_start>2025-06-15T18:00:00+00:00'


def fetch_latest_session(session: Session) -> str:
    result = session.exec(
        select(F1Session.date).order_by(desc(F1Session.date))
    ).first()
    return result

def fetch_meeting_keys(session:Session) -> set:
    results = session.exec(select(Event.meeting_key)).all()
    return set(results)

#returns true if successfuly added meeting key to db
def add_meeting_to_db(session: Session, meeting_key:int):
    meeting_data = get_data(URL_BASE + f'meetings?meeting_key={str(meeting_key)}')
    #todo check what this returns

def add_session_to_db(session:Session, session_key:int):
    pass

def add_driver_laps_to_db(session:Session, session_key:int):
    pass

def update_db(latest_session_date: str):
    url = URL_BASE + f'sessions?date_start>{latest_session_date}'
    data = get_data(url)

    with Session(engine) as session:
        meeting_keys = fetch_meeting_keys(session)
        for f1session in data:
            if not f1session['meeting_key'] in meeting_keys:
                added = True if add_meeting_to_db(session, f1session['meeting_key']) else False
                if added:
                    meeting_keys.add(f1session['meeting_key'])
                add_session_to_db(session, f1session['session_key'])
                add_driver_laps_to_db(session, f1session['session_key'])

#with next(get_session()) as s:
#    print(f"session: {fetch_latest_session(s)}")
