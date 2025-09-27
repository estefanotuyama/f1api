from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.api import sessions, events, drivers, laps
from backend.db.database import create_db_and_tables

BASE_DIR = Path(__file__).resolve().parent.parent  # project root
app = FastAPI(title="F1 Stats",
              description="Simple app for F1 statistics")
app.include_router(events.router)
app.include_router(sessions.router)
app.include_router(drivers.router)
app.include_router(laps.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # frontend dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables(populating=False)

@app.get("/")
async def root():
    return {"message": "Welcome to F1 Stats API!"}

@app.get("/favicon.ico")
def favicon():
    return FileResponse(BASE_DIR / "static" / "favicon.ico")  # ✅ correct
