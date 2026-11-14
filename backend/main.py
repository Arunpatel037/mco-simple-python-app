import os
import sqlite3
from contextlib import asynccontextmanager, closing
from typing import Annotated

from fastapi import FastAPI
from pydantic import BaseModel, StringConstraints

DB_PATH = os.getenv("DB_PATH", "app.db")


def run_query(sql, params=()):
    # Open a connection, run one statement, commit and close.
    with closing(sqlite3.connect(DB_PATH)) as conn, conn:
        conn.row_factory = sqlite3.Row
        return conn.execute(sql, params).fetchone()


@asynccontextmanager
async def db_init(app):
    # Create the table on first start and add the default message once.
    run_query("CREATE TABLE IF NOT EXISTS greeting (id INTEGER PRIMARY KEY, message TEXT NOT NULL)")
    run_query("INSERT OR IGNORE INTO greeting (id, message) VALUES (1, 'Hello World')")
    yield


app = FastAPI(lifespan=db_init)


class update_message(BaseModel):
    # Trim spaces and allow 1 to 200 characters.
    message: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]


@app.get("/healthz")
def health_check():
    return {"status": "ok"}


@app.get("/api/greeting")
def get_greeting():
    return dict(run_query("SELECT message FROM greeting WHERE id = 1"))


@app.put("/api/greeting")
def update_greeting(greeting: update_message):
    row = run_query("UPDATE greeting SET message = ? WHERE id = 1 RETURNING message", (greeting.message,))
    return dict(row)
