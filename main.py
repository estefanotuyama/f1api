from fastapi import FastAPI

from api import events, sessions
from db.database import create_db_and_tables

app = FastAPI(title="F1 Stats",
              description="Simple app for F1 statistics")

app.include_router(events.router)
app.include_router(sessions.router)

@app.on_event("startup")
def on_startup():
    create_db_and_tables(populating=False)


@app.get("/")
async def root():
    return {"message": "Welcome to F1 Stats!"}