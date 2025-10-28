# app.py — Flask wiring (v4.1 parity patch)
from __future__ import annotations
from flask import Flask, render_template, request, redirect, url_for, session
from game_logic import Game
import os
from uuid import uuid4

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-key")

# In-memory store keyed by session id (simple & fine for single-player)
GAMES = {}

def _sid() -> str:
    sid = session.get("sid")
    if not sid:
        sid = str(uuid4())
        session["sid"] = sid
    return sid

def _game() -> Game:
    sid = _sid()
    if sid not in GAMES:
        GAMES[sid] = Game()
    return GAMES[sid]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/new_game/<difficulty>")
def new_game(difficulty):
    # You can tune difficulty to set max_turns / starting stats
    g = Game()
    if difficulty == "easy":
        g.max_turns = 30
        g.stability = 70
    elif difficulty == "hard":
        g.max_turns = 16
        g.stability = 60
        g.collapse = 50
    # else normal defaults

    GAMES[_sid()] = g
    return redirect(url_for("game"))


@app.route("/game")
def game():
    g = _game()
    return render_template("game.html", state=g.to_dict())


@app.post("/action")
def action():
    g = _game()
    a = request.form.get("type", "")

    # NOTE: every action returns True/False to indicate success;
    # we DO NOT advance the turn here.
    success = False

    if a == "harvest":
        success = g.harvest_free()
    elif a == "gather_timber":
        success = g.gather_timber()
    elif a == "fortify":
        success = g.fortify()
    elif a == "withdraw":
        success = g.withdraw_support()
    elif a == "research_ib":
        success = g.research_imperial_bureaucracy()
    elif a == "build_mine":
        success = g.build_bronze_mine()
    else:
        g._log("Action cancelled.", "secondary")
        success = False  # never advance on cancel

    return redirect(url_for("game"))


@app.post("/choice")
def choice():
    g = _game()
    choice_value = request.form.get("choice", "")
    
    if choice_value in ["a", "b"]:
        g.resolve_choice(choice_value)
    
    return redirect(url_for("game"))


@app.post("/end_turn")
def end_turn():
    g = _game()
    # End turn ONLY if both action flags used; otherwise stay on same turn.
    if not g.end_turn():
        # messages already added by can_end_turn(); just re-render
        return redirect(url_for("game"))

    # Check victory/defeat
    if g.turn > g.max_turns and g.collapse >= 80 and g.military >= 50:
        # Vacuum victory
        session["victory"] = {"type": "vacuum", "final": g.to_dict()}
        return redirect(url_for("victory"))
    if g.stability <= 0 or g.military <= 0:
        session["victory"] = {"type": "defeat", "final": g.to_dict()}
        return redirect(url_for("victory"))
    if g.collapse == 0:
        session["victory"] = {"type": "preservation", "final": g.to_dict()}
        return redirect(url_for("victory"))

    return redirect(url_for("game"))


@app.get("/victory")
def victory():
    data = session.get("victory")
    if not data:
        return redirect(url_for("game"))
    return render_template("victory.html", result=data)


if __name__ == "__main__":
    app.run(debug=True)
