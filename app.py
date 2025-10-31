# app.py — Flask wiring (v4.1 parity patch)
from __future__ import annotations
from flask import Flask, render_template, request, redirect, url_for, session
from game_logic import Game
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-key")

# Use Flask session storage for game state (works with serverless/Vercel)

def _game() -> Game:
    """Get or create game from session storage"""
    try:
        if "game" not in session:
            logger.info("Creating new game")
            game = Game()
            session["game"] = game.to_dict()
            return game
        else:
            # Reconstruct game from session
            game = Game.from_dict(session["game"])
            return game
    except Exception as e:
        logger.error(f"Error in _game: {e}", exc_info=True)
        # Create new game as fallback
        game = Game()
        session["game"] = game.to_dict()
        return game

def _save_game(game: Game) -> None:
    """Save game state to session"""
    try:
        session["game"] = game.to_dict()
        session.modified = True
    except Exception as e:
        logger.error(f"Error saving game: {e}", exc_info=True)


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
        _save_game(g)
        logger.info(f"Game initialized with difficulty: {difficulty}")
        
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
            logger.error("Invalid game state detected - missing required attributes")
            # Create new game as fallback
            g = Game()
            g._log("Game state was invalid - created new game.", "warning")
            _save_game(g)
        
        # Additional validation checks
        if g.turn < 1:
            logger.warning(f"Invalid turn number {g.turn}, resetting to 1")
            g.turn = 1
        
        if g.max_turns < g.turn:
            logger.warning(f"Turn {g.turn} exceeds max_turns {g.max_turns}")
            # Don't reset, just log - game may be in end state
        
        # Check for victory/defeat conditions on game view load
        game_result = g._check_game_end()
        if game_result:
            logger.info(f"Game ended on view load: {game_result}")
            session["victory"] = {"type": game_result["type"], "reason": game_result.get("reason"), "final": g.to_dict()}
            _save_game(g)
            return redirect(url_for("victory"))
        
        # Pass game state to template
        return render_template("game.html", game=g.to_dict())
    except Exception as e:
        logger.error(f"Error in game route: {e}", exc_info=True)
        # Try to create a fresh game
        try:
            g = Game()
            _save_game(g)
            logger.info("Created new game after error")
            return redirect(url_for("game"))
        except Exception as recovery_error:
            logger.error(f"Could not recover from game error: {recovery_error}", exc_info=True)
            # Last resort - redirect to index
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

        # Basic actions
        if a == "harvest":
            success = g.harvest_free()
        elif a == "gather_timber":
            success = g.gather_timber()
        elif a == "fortify":
            success = g.fortify()
        elif a == "withdraw":
            success = g.withdraw_support()
        # Research
        elif a == "research_ib":
            success = g.research_imperial_bureaucracy()
        elif a == "research_tin_trade":
            success = g.research_tin_trade_routes()
        elif a == "research_phalanx":
            success = g.research_phalanx_formation()
        elif a == "research_marriage":
            success = g.research_diplomatic_marriage()
        # Buildings
        elif a == "build_mine":
            success = g.build_bronze_mine()
        elif a == "build_granary":
            success = g.build_granary()
        elif a == "build_barracks":
            success = g.build_barracks()
        elif a == "build_palace":
            success = g.build_palace()
        elif a == "build_lighthouse":
            success = g.build_lighthouse()
        elif a == "build_watchtower":
            success = g.build_watchtower()
        # Diplomacy
        elif a == "send_tribute":
            target = request.form.get("target", "egypt")
            success = g.send_tribute(target)
        elif a == "form_alliance":
            success = g.form_alliance()
        elif a == "host_festival":
            success = g.host_festival()
        else:
            logger.warning(f"Unknown or cancelled action: {a}")
            g._log("Action cancelled.", "secondary")
            success = False  # never advance on cancel
        
        logger.info(f"Action {a} result: {success}")

        if not success:
            logger.warning(f"Action {a} failed - check game state or resources")

        # Save game state after action
        _save_game(g)
        return redirect(url_for("game"))
    except Exception as e:
        logger.error(f"Error in action route: {e}", exc_info=True)
        # Add error message to game log if possible
        try:
            g = _game()
            g._log("An error occurred processing your action. Please try again.", "danger")
            _save_game(g)
        except Exception as log_error:
            logger.error(f"Could not add error message to game log: {log_error}")
        return redirect(url_for("game"))


@app.post("/choice")
def choice():
    """Handle player choice events"""
    try:
        g = _game()
        choice_value = request.form.get("choice", "")
        logger.info(f"Processing choice: {choice_value} for turn {g.turn}")

        if choice_value in ["a", "b"]:
            # Attempt to resolve the choice
            if not g.resolve_choice(choice_value):
                logger.warning(f"Choice {choice_value} resolution failed - likely insufficient resources")
                # Message already added by resolve_choice
                _save_game(g)
                return redirect(url_for("game"))
            
            logger.info(f"Choice {choice_value} resolved successfully")
            
            # Auto-advance turn if both actions are complete
            if g.free_harvest_used and g.paid_action_used:
                logger.info("Both actions complete after choice - auto-advancing turn")
                if g.end_turn():
                    logger.info(f"Turn auto-advanced to {g.turn}")
                    
                    # Check for victory/defeat conditions after auto-advance using centralized function
                    game_result = g._check_game_end()
                    if game_result:
                        logger.info(f"Game ended after choice: {game_result}")
                        session["victory"] = {"type": game_result["type"], "reason": game_result.get("reason"), "final": g.to_dict()}
                        _save_game(g)
                        return redirect(url_for("victory"))
                else:
                    logger.warning("Failed to auto-advance turn after choice")
        else:
            logger.warning(f"Invalid choice value: {choice_value}")
            g._log("Invalid choice selected.", "danger")

        # Save game state after choice
        _save_game(g)
        return redirect(url_for("game"))
    except Exception as e:
        logger.error(f"Error in choice route: {e}", exc_info=True)
        # Try to add error message to game
        try:
            g = _game()
            g._log("An error occurred processing your choice. Please try again.", "danger")
            _save_game(g)
        except Exception as log_error:
            logger.error(f"Could not add error message to game log: {log_error}")
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
            _save_game(g)
            return redirect(url_for("game"))

        logger.info(f"Turn {g.turn - 1} ended successfully, now on turn {g.turn}")

        # Check victory/defeat conditions using centralized function
        try:
            game_result = g._check_game_end()
            if game_result:
                logger.info(f"Game ended: {game_result}")
                session["victory"] = {"type": game_result["type"], "reason": game_result.get("reason"), "final": g.to_dict()}
                _save_game(g)
                return redirect(url_for("victory"))
        except Exception as victory_check_error:
            logger.error(f"Error checking victory conditions: {victory_check_error}", exc_info=True)
            # Continue to game even if victory check failed

        # Save game state after turn advancement
        _save_game(g)
        return redirect(url_for("game"))
    except Exception as e:
        logger.error(f"Error in end_turn route: {e}", exc_info=True)
        # Try to add error message
        try:
            g = _game()
            g._log("An error occurred ending the turn. Please try again.", "danger")
            _save_game(g)
        except Exception as log_error:
            logger.error(f"Could not add error message: {log_error}")
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
