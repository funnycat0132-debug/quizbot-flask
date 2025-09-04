from flask import Flask, render_template, request, redirect, url_for, session
import time

app = Flask(__name__)
app.secret_key = "замени-на-свой-секрет"

# Название теста
TEST_TITLE = "R-RP 07 Тест на 9-й ранг"

# База вопросов
questions = [
    {"q": "Столица Франции?", "opts": ["Берлин", "Париж", "Рим", "Мадрид"], "a": 1},
    {"q": "2 + 2 = ?", "opts": ["3", "4", "5", "6"], "a": 1},
]

@app.route("/")
def index():
    session["start_time"] = time.time()
    session["score"] = 0
    session["index"] = 0
    return render_template("index.html", title=TEST_TITLE)

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if "start_time" not in session:
        return redirect(url_for("index"))

    # Ограничение по времени (30 сек на весь тест)
    if time.time() - session["start_time"] > 30:
        return redirect(url_for("result"))

    if request.method == "POST":
        answer = int(request.form["answer"])
        q = questions[session["index"]]
        if answer == q["a"]:
            session["score"] += 1
        session["index"] += 1

    if session["index"] >= len(questions):
        return redirect(url_for("result"))

    q = questions[session["index"]]
    return render_template("quiz.html", q=q, idx=session["index"], title=TEST_TITLE)

@app.route("/result")
def result():
    return f"Тест завершён! Очки: {session['score']} из {len(questions)}"

if __name__ == "__main__":
    app.run(debug=True)