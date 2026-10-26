#!/usr/bin/env python3
"""State store for the Nightly Stretching Routine app.

Keeps the app's full state (one JSON document) in a SQLite database on the
Pi, so the same routine shows up no matter which browser or app context
opens the page. The app stamps every save with a `savedAt` timestamp and
the newest one wins; this server just stores and returns it.

Endpoints:
  GET  /api/health  -> {"ok": true}
  GET  /api/state   -> {"savedAt": <ms epoch>, "state": {...}} or 404
  PUT  /api/state   <- {"savedAt": <ms epoch>, "state": {...}}
                       stores only if savedAt is not older than what's kept;
                       replies {"savedAt": <the stored timestamp>}
                       A savedAt more than 5 minutes ahead of the server's
                       own clock is clamped to the server's time, so one
                       fast-clock client can't poison the store.

Standard library only — no dependencies.
"""
import json
import os
import sqlite3
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

DB_PATH = os.environ.get("STATE_DB", "/data/state.db")


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS app_state ("
        " id INTEGER PRIMARY KEY CHECK (id = 1),"
        " saved_at INTEGER NOT NULL,"
        " state TEXT NOT NULL)"
    )
    return conn


def get_state():
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT saved_at, state FROM app_state WHERE id = 1"
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        return None
    return {"savedAt": row[0], "state": json.loads(row[1])}


def put_state(saved_at, state):
    now_ms = int(time.time() * 1000)
    if saved_at > now_ms + 5 * 60 * 1000:
        saved_at = now_ms
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT saved_at FROM app_state WHERE id = 1"
        ).fetchone()
        if row is None or saved_at >= row[0]:
            conn.execute(
                "INSERT INTO app_state (id, saved_at, state) VALUES (1, ?, ?)"
                " ON CONFLICT(id) DO UPDATE SET"
                " saved_at = excluded.saved_at, state = excluded.state",
                (saved_at, json.dumps(state)),
            )
            conn.commit()
            return saved_at
        return row[0]
    finally:
        conn.close()


class Handler(BaseHTTPRequestHandler):
    def _reply(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/health":
            self._reply(200, {"ok": True})
        elif self.path == "/api/state":
            rec = get_state()
            if rec is None:
                self._reply(404, {"error": "empty"})
            else:
                self._reply(200, rec)
        else:
            self._reply(404, {"error": "not found"})

    def do_PUT(self):
        if self.path != "/api/state":
            self._reply(404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length") or 0)
            payload = json.loads(self.rfile.read(length) or b"{}")
            saved_at = int(payload.get("savedAt") or 0)
            state = payload.get("state")
            if state is None:
                raise ValueError("missing state")
        except Exception:
            self._reply(400, {"error": "bad request"})
            return
        self._reply(200, {"savedAt": put_state(saved_at, state)})

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    ThreadingHTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
