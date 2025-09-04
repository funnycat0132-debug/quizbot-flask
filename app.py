
import os
import time
import json
import random
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, g

APP_SECRET = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")
TEST_DURATION_SECONDS = int(os.environ.get("TEST_DURATION_SECONDS", "120"))
DATABASE_PATH = os.environ.get("DATABASE_PATH", "quiz.db")

app = Flask(__name__)
app.secret_key = APP_SECRET

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    db.execute(
        """CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            started_at TEXT,
            finished_at TEXT,
            score INTEGER,
            total INTEGER,
            duration_sec INTEGER,
            client_ip TEXT
        )"""
    )
    db.commit()

def load_questions():
    with open("questions.json", "r", encoding="utf-8") as f:
        return json.load(f)

QUESTIONS = load_questions()

@app.before_first_request
def setup():
    init_db()

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", total=len(QUESTIONS), duration=TEST_DURATION_SECONDS)

@app.route("/start", methods=["POST"])
def start():
    # initialize a new test session
    session.clear()
    session["start_time"] = time.time()
    session["index"] = 0
    session["score"] = 0
    order = list(range(len(QUESTIONS)))
    random.shuffle(order)
    session["order"] = order
    session["finished_saved"] = False
    return redirect(url_for("quiz"))

def time_left():
    if "start_time" not in session:
        return 0
    elapsed = time.time() - session["start_time"]
    left = int(TEST_DURATION_SECONDS - elapsed)
    return max(0, left)

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if "start_time" not in session:
        return redirect(url_for("index"))

    if time_left() <= 0:
        return redirect(url_for("result"))

    if request.method == "POST":
        # handle answer
        try:
            answer = int(request.form.get("answer", "-1"))
        except ValueError:
            answer = -1

        idx = session["order"][session["index"]]
        q = QUESTIONS[idx]
        correct = q["answer"]
        if answer == correct:
            session["score"] += 1
        session["index"] += 1

        if session["index"] >= len(QUESTIONS):
            return redirect(url_for("result"))
        else:
            return redirect(url_for("quiz"))

    # GET: render question
    idx = session["order"][session["index"]]
    q = QUESTIONS[idx]
    deadline_ts = int(session["start_time"]) + TEST_DURATION_SECONDS
    return render_template(
        "quiz.html",
        q=q,
        idx=session["index"],
        total=len(QUESTIONS),
        time_left=time_left(),
        deadline=deadline_ts
    )

@app.route("/result", methods=["GET"])
def result():
    if "start_time" not in session:
        return redirect(url_for("index"))

    total = len(QUESTIONS)
    score = session.get("score", 0)
    started_at = datetime.fromtimestamp(session["start_time"]).isoformat(timespec="seconds")
    finished_at = datetime.now().isoformat(timespec="seconds")
    duration_sec = TEST_DURATION_SECONDS - time_left()

    # Save once
    if not session.get("finished_saved", False):
        db = get_db()
        db.execute(
            "INSERT INTO results (started_at, finished_at, score, total, duration_sec, client_ip) VALUES (?, ?, ?, ?, ?, ?)",
            (started_at, finished_at, score, total, duration_sec, request.headers.get("X-Forwarded-For", request.remote_addr))
        )
        db.commit()
        session["finished_saved"] = True

    return render_template("result.html", score=score, total=total, started_at=started_at, finished_at=finished_at, duration_sec=duration_sec)

@app.route("/healthz")
def healthz():
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
