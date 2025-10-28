# app.py — Flask wiring (v4.1 parity patch)
from __future__ import annotations
from flask import Flask, render_template, request, redirect, url_for, session
from game_logic import Game
import os
import logging
from uuid import uuid4

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-key")

# In-memory store keyed by session id (simple & fine for single-player)
GAMES = {}

def _sid() -> str:
    """Get or create session ID"""
    try:
        sid = session.get("sid")
        if not sid:
            sid = str(uuid4())
            session["sid"] = sid
            logger.info(f"Created new session: {sid}")
        return sid
    except Exception as e:
        logger.error(f"Error in _sid: {e}")
        # Create fallback session ID
        sid = str(uuid4())
        session["sid"] = sid
        return sid

def _game() -> Game:
    """Get or create game for current session"""
    try:
        sid = _sid()
        if sid not in GAMES:
            logger.info(f"Creating new game for session: {sid}")
            GAMES[sid] = Game()
        return GAMES[sid]
    except Exception as e:
        logger.error(f"Error in _game: {e}")
        # Create a new game as fallback
        sid = _sid()
        GAMES[sid] = Game()
        return GAMES[sid]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/new_game/<difficulty>")
def new_game(difficulty):
    """Initialize a new game with selected difficulty"""
    try:
        logger.info(f"Starting new game with difficulty: {difficulty}")
        
        # Validate difficulty
        if difficulty not in ["easy", "normal", "hard"]:
            logger.warning(f"Invalid difficulty: {difficulty}, defaulting to normal")
            difficulty = "normal"
        
        # Create new game
        g = Game()
        g.difficulty = difficulty  # Set difficulty
        
        # Apply difficulty settings
        if difficulty == "easy":
            g.max_turns = 30
            g.stability = 70
            logger.info("Applied easy difficulty settings")
        elif difficulty == "hard":
            g.max_turns = 16
            g.stability = 60
            g.collapse = 50
            logger.info("Applied hard difficulty settings")
        else:
            logger.info("Using normal difficulty settings")
        
        # Store game in session
        sid = _sid()
        GAMES[sid] = g
        logger.info(f"Game initialized for session {sid}")
        
        return redirect(url_for("game"))
    except Exception as e:
        logger.error(f"Error in new_game: {e}", exc_info=True)
        # Try to return to index with error message
        return redirect(url_for("index"))


@app.route("/game")
def game():
    """Main game view"""
    try:
        g = _game()
        logger.info(f"Rendering game view for turn {g.turn}")
        
        # Validate game state
        if not hasattr(g, 'turn') or not hasattr(g, 'to_dict'):
            logger.error("Invalid game state detected")
            return redirect(url_for("index"))
        
        # Pass game state to template
        return render_template("game.html", game=g.to_dict())
    except Exception as e:
        logger.error(f"Error in game route: {e}", exc_info=True)
        # Try to create a new game
        try:
            sid = _sid()
            GAMES[sid] = Game()
            g = GAMES[sid]
            return render_template("game.html", game=g.to_dict())
        except Exception as e2:
            logger.error(f"Failed to recover from error: {e2}", exc_info=True)
            return redirect(url_for("index"))


@app.post("/action")
def action():
    """Handle player actions"""
    try:
        g = _game()
        a = request.form.get("type", "")
        logger.info(f"Processing action: {a} for turn {g.turn}")

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
        
        logger.info(f"Action {a} result: {success}")
        return redirect(url_for("game"))
    except Exception as e:
        logger.error(f"Error in action route: {e}", exc_info=True)
        return redirect(url_for("game"))


@app.post("/choice")
def choice():
    """Handle player choice events"""
    try:
        g = _game()
        choice_value = request.form.get("choice", "")
        logger.info(f"Processing choice: {choice_value} for turn {g.turn}")

        if choice_value in ["a", "b"]:
            g.resolve_choice(choice_value)
            logger.info(f"Choice {choice_value} resolved successfully")
        else:
            logger.warning(f"Invalid choice value: {choice_value}")

        return redirect(url_for("game"))
    except Exception as e:
        logger.error(f"Error in choice route: {e}", exc_info=True)
        return redirect(url_for("game"))


@app.post("/end_turn")
def end_turn():
    """Handle end turn and check for victory/defeat conditions"""
    try:
        g = _game()
        logger.info(f"Attempting to end turn {g.turn}")
        
        # End turn ONLY if both action flags used; otherwise stay on same turn.
        if not g.end_turn():
            # messages already added by can_end_turn(); just re-render
            logger.info(f"Cannot end turn {g.turn} - conditions not met")
            return redirect(url_for("game"))

        logger.info(f"Turn {g.turn - 1} ended successfully, now on turn {g.turn}")

        # Check victory/defeat
        if g.turn > g.max_turns and g.collapse >= 80 and g.military >= 50:
            # Vacuum victory
            logger.info("Vacuum victory achieved")
            session["victory"] = {"type": "vacuum", "final": g.to_dict()}
            return redirect(url_for("victory"))
        if g.stability <= 0 or g.military <= 0:
            logger.info("Defeat condition met")
            session["victory"] = {"type": "defeat", "final": g.to_dict()}
            return redirect(url_for("victory"))
        if g.collapse == 0:
            logger.info("Preservation victory achieved")
            session["victory"] = {"type": "preservation", "final": g.to_dict()}
            return redirect(url_for("victory"))

        return redirect(url_for("game"))
    except Exception as e:
        logger.error(f"Error in end_turn route: {e}", exc_info=True)
        return redirect(url_for("game"))


@app.get("/victory")
def victory():
    """Display victory/defeat screen"""
    try:
        data = session.get("victory")
        if not data:
            logger.warning("Victory route accessed without victory data")
            return redirect(url_for("game"))
        logger.info(f"Displaying victory screen: {data.get('type')}")
        return render_template("victory.html", result=data)
    except Exception as e:
        logger.error(f"Error in victory route: {e}", exc_info=True)
        return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
