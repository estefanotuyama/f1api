from fastapi import FastAPI
from database import create_db_and_tables

app = FastAPI(title="F1 Stats",
              description="Simple app for F1 statistics")

@app.on_event("startup")
def on_startup():
    create_db_and_tables(populating=False)


@app.get("/")
async def root():
    return {"message": "Hello World"}