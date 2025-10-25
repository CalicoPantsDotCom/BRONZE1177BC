"""
BRONZE: 1177 BC - Flask Web App
v1.2.6 - Web Edition
"""

from flask import Flask, render_template, session, redirect, url_for, request, jsonify
from game_logic import GameState
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'bronze-1177-bc-secret-key-change-in-production')

def get_game():
    """Get or create game state from session"""
    if 'game' not in session:
        game = GameState()
        session['game'] = game.to_dict()
    else:
        game = GameState.from_dict(session['game'])
    return game

def save_game(game):
    """Save game state to session"""
    session['game'] = game.to_dict()
    session.modified = True

@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@app.route('/new_game')
@app.route('/new_game/<difficulty>')
def new_game(difficulty='normal'):
    """Start a new game with selected difficulty"""
    game = GameState(difficulty=difficulty)
    session['game'] = game.to_dict()
    return redirect(url_for('game'))

@app.route('/game')
def game():
    """Main game interface"""
    game = get_game()

    if game.game_over:
        return redirect(url_for('victory'))

    return render_template('game.html', game=game)

@app.route('/action/<action_name>', methods=['POST'])
def action(action_name):
    """Handle player actions"""
    game = get_game()
    game.clear_messages()

    success = False

    # Direct actions
    # HARVEST IS FREE - doesn't advance turn
    if action_name == 'harvest':
        success = game.harvest()
    # All other actions cost the turn (handled in end_turn route)
    elif action_name == 'gather_timber':
        success = game.gather_timber()
    elif action_name == 'fortify':
        success = game.fortify()

    # Building actions
    elif action_name == 'build_bronze_mine':
        success = game.build_bronze_mine()
    elif action_name == 'build_granary':
        success = game.build_granary()
    elif action_name == 'build_barracks':
        success = game.build_barracks()
    elif action_name == 'build_palace':
        success = game.build_palace()
    elif action_name == 'build_lighthouse':
        success = game.build_lighthouse()
    elif action_name == 'build_watchtower':
        success = game.build_watchtower()

    # Research actions
    elif action_name == 'research_imperial_bureaucracy':
        success = game.research_imperial_bureaucracy()
    elif action_name == 'research_tin_trade_routes':
        success = game.research_tin_trade_routes()
    elif action_name == 'research_phalanx_formation':
        success = game.research_phalanx_formation()
    elif action_name == 'research_diplomatic_marriage':
        success = game.research_diplomatic_marriage()

    # Diplomacy actions
    elif action_name == 'send_tribute':
        success = game.send_tribute()
    elif action_name == 'form_alliance':
        success = game.form_alliance()
    elif action_name == 'host_festival':
        success = game.host_festival()

    # Withdraw action
    elif action_name == 'withdraw':
        success = game.withdraw_from_alliance()

    # DO NOT auto-advance turn anymore
    # Player must click "End Turn" button

    save_game(game)

    # Return JSON for AJAX updates
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': success,
            'game_over': game.game_over,
            'messages': game.message_log,
            'game': game.to_dict()
        })

    return redirect(url_for('game'))

@app.route('/end_turn', methods=['POST'])
def end_turn_route():
    """End the current turn"""
    game = get_game()
    game.clear_messages()

    # Process end-of-turn
    game.end_turn()

    save_game(game)
    return redirect(url_for('game'))

@app.route('/victory')
def victory():
    """Victory/defeat screen"""
    game = get_game()
    return render_template('victory.html', game=game)

@app.route('/api/game_state')
def api_game_state():
    """API endpoint for game state"""
    game = get_game()
    return jsonify(game.to_dict())

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
