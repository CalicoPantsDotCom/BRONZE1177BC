"""
Core game logic for BRONZE: 1177 BC
Ported from v1.2.6 CLI version
"""

import random

class GameState:
    def __init__(self, difficulty='normal'):
        # Resources
        self.grain = 50
        self.timber = 20
        self.bronze = 10

        # Core Metrics
        self.military = 20
        self.stability = 60
        self.prestige = 30

        # Crisis
        self.collapse = 50

        # Buildings
        self.has_bronze_mine = False
        self.has_granary = False
        self.has_barracks = False
        self.has_palace = False
        self.has_lighthouse = False
        self.has_watchtower = False

        # Technologies
        self.has_imperial_bureaucracy = False
        self.has_tin_trade_routes = False
        self.has_phalanx_formation = False
        self.has_diplomatic_marriage = False

        # Game state
        self.turn = 1
        self.difficulty = difficulty
        self.max_turns = {'easy': 30, 'normal': 20, 'hard': 15}.get(difficulty, 20)
        self.game_over = False
        self.victory_type = None
        self.message_log = []

        # Action tracking (NEW)
        self.current_turn_actions = []  # Actions taken this turn
        self.previous_turn_summary = None  # Summary of last turn
        self.turn_history = []  # Full history of all turns

        # Turn action tracking (v2.3)
        self.has_used_free_harvest = False  # One free harvest per turn
        self.has_taken_paid_action = False  # One paid action required per turn

    def to_dict(self):
        """Serialize game state for session storage"""
        return {
            'grain': self.grain,
            'timber': self.timber,
            'bronze': self.bronze,
            'military': self.military,
            'stability': self.stability,
            'prestige': self.prestige,
            'collapse': self.collapse,
            'has_bronze_mine': self.has_bronze_mine,
            'has_granary': self.has_granary,
            'has_barracks': self.has_barracks,
            'has_palace': self.has_palace,
            'has_lighthouse': self.has_lighthouse,
            'has_watchtower': self.has_watchtower,
            'has_imperial_bureaucracy': self.has_imperial_bureaucracy,
            'has_tin_trade_routes': self.has_tin_trade_routes,
            'has_phalanx_formation': self.has_phalanx_formation,
            'has_diplomatic_marriage': self.has_diplomatic_marriage,
            'turn': self.turn,
            'difficulty': self.difficulty,
            'max_turns': self.max_turns,
            'game_over': self.game_over,
            'victory_type': self.victory_type,
            'message_log': self.message_log,
            'current_turn_actions': self.current_turn_actions,
            'previous_turn_summary': self.previous_turn_summary,
            'turn_history': self.turn_history,
            'has_used_free_harvest': self.has_used_free_harvest,
            'has_taken_paid_action': self.has_taken_paid_action
        }

    @classmethod
    def from_dict(cls, data):
        """Deserialize game state from session storage"""
        game = cls()
        for key, value in data.items():
            if hasattr(game, key):
                setattr(game, key, value)
        return game

    def add_message(self, message, msg_type="info"):
        """Add message to log with type (success, warning, danger, info)"""
        self.message_log.append({'text': message, 'type': msg_type})

    def clear_messages(self):
        """Clear message log"""
        self.message_log = []

    def log_action(self, action_name, effects):
        """Log an action taken this turn"""
        self.current_turn_actions.append({
            'name': action_name,
            'effects': effects
        })

    def check_and_auto_end_turn(self):
        """Check if turn should auto-end (both free harvest and paid action taken)"""
        if self.has_used_free_harvest and self.has_taken_paid_action:
            self.add_message("✓ Turn complete! Processing end-of-turn...", "info")
            self.end_turn()
            return True
        return False

    # Actions
    def harvest(self):
        """Action: Harvest (+15 Grain, +10 Bronze) - First one FREE, second costs turn"""
        if not self.has_used_free_harvest:
            # First harvest is FREE
            self.grain += 15
            self.bronze += 10
            self.has_used_free_harvest = True
            self.log_action("Harvest (FREE)", "+15 Grain, +10 Bronze")
            self.add_message("✓ Harvested: +15 Grain, +10 Bronze (FREE)", "success")
            self.check_and_auto_end_turn()
            return True
        elif not self.has_taken_paid_action:
            # Second harvest costs the paid action (only if no paid action taken yet)
            self.grain += 15
            self.bronze += 10
            self.has_taken_paid_action = True
            self.log_action("Harvest", "+15 Grain, +10 Bronze (paid action)")
            self.add_message("✓ Harvested: +15 Grain, +10 Bronze (used paid action)", "success")
            self.check_and_auto_end_turn()
            return True
        else:
            # Can't harvest - already used free harvest AND took a paid action
            self.add_message("❌ You've already taken your paid action this turn!", "danger")
            return False

    def gather_timber(self):
        """Action: Gather Timber (-8 Grain → +10 Timber) - First one FREE, second costs turn"""
        if not self.has_used_free_harvest:
            # First gather is FREE
            if self.grain < 8:
                self.add_message("Insufficient Grain! Need 8 Grain.", "danger")
                return False
            self.grain -= 8
            self.timber += 10
            self.has_used_free_harvest = True
            self.log_action("Gather Timber (FREE)", "-8 Grain, +10 Timber")
            self.add_message("✓ Gathered Timber: -8 Grain, +10 Timber (FREE)", "success")
            self.check_and_auto_end_turn()
            return True
        elif not self.has_taken_paid_action:
            # Second gather costs the paid action (only if no paid action taken yet)
            if self.grain < 8:
                self.add_message("Insufficient Grain! Need 8 Grain.", "danger")
                return False
            self.grain -= 8
            self.timber += 10
            self.has_taken_paid_action = True
            self.log_action("Gather Timber", "-8 Grain, +10 Timber (paid action)")
            self.add_message("✓ Gathered Timber: -8 Grain, +10 Timber (used paid action)", "success")
            self.check_and_auto_end_turn()
            return True
        else:
            # Can't gather - already used free harvest AND took a paid action
            self.add_message("❌ You've already taken your paid action this turn!", "danger")
            return False

    def fortify(self):
        """Action: Fortify (+5 Military, -5 Stability) - PAID ACTION"""
        if self.has_taken_paid_action:
            self.add_message("❌ You've already taken your paid action this turn!", "danger")
            return False

        self.military += 5
        self.stability -= 5
        self.has_taken_paid_action = True
        self.log_action("Fortify", "+5 Military, -5 Stability")
        self.add_message("✓ Fortified: +5 Military, -5 Stability", "success")
        self.check_and_auto_end_turn()
        return True

    # Building actions
    def build_bronze_mine(self):
        if self.has_taken_paid_action:
            self.add_message("❌ You've already taken your paid action this turn!", "danger")
            return False
        if self.has_bronze_mine:
            self.add_message("Bronze Mine already built!", "warning")
            return False
        if self.grain < 15 or self.timber < 10:
            self.add_message("Insufficient resources! Need 15 Grain, 10 Timber.", "danger")
            return False

        self.grain -= 15
        self.timber -= 10
        self.has_bronze_mine = True
        self.has_taken_paid_action = True
        self.log_action("Build Bronze Mine", "-15 Grain, -10 Timber | +2 Bronze/turn")
        self.add_message("✓ Bronze Mine built! +2 Bronze per turn.", "success")
        self.check_and_auto_end_turn()
        return True

    def build_granary(self):
        if self.has_taken_paid_action:
            self.add_message("❌ You've already taken your paid action this turn!", "danger")
            return False
        if self.has_granary:
            self.add_message("Granary already built!", "warning")
            return False
        if self.grain < 20 or self.timber < 15:
            self.add_message("Insufficient resources! Need 20 Grain, 15 Timber.", "danger")
            return False

        self.grain -= 20
        self.timber -= 15
        self.has_granary = True
        self.has_taken_paid_action = True
        self.log_action("Build Granary", "-20 Grain, -15 Timber | +3 Grain/turn")
        self.add_message("✓ Granary built! +3 Grain per turn.", "success")
        self.check_and_auto_end_turn()
        return True

    def build_barracks(self):
        if self.has_taken_paid_action:
            self.add_message("❌ You've already taken your paid action this turn!", "danger")
            return False
        if self.has_barracks:
            self.add_message("Barracks already built!", "warning")
            return False
        if self.grain < 25 or self.timber < 20 or self.bronze < 10:
            self.add_message("Insufficient resources! Need 25 Grain, 20 Timber, 10 Bronze.", "danger")
            return False

        self.grain -= 25
        self.timber -= 20
        self.bronze -= 10
        self.has_barracks = True
        self.has_taken_paid_action = True
        self.log_action("Build Barracks", "-25 Grain, -20 Timber, -10 Bronze | +2 Military/turn")
        self.add_message("✓ Barracks built! +2 Military per turn.", "success")
        self.check_and_auto_end_turn()
        return True

    def build_palace(self):
        if self.has_taken_paid_action:
            self.add_message("❌ You've already taken your paid action this turn!", "danger")
            return False
        if self.has_palace:
            self.add_message("Palace already built!", "warning")
            return False
        if self.grain < 30 or self.timber < 25 or self.bronze < 15:
            self.add_message("Insufficient resources! Need 30 Grain, 25 Timber, 15 Bronze.", "danger")
            return False

        self.grain -= 30
        self.timber -= 25
        self.bronze -= 15
        self.has_palace = True
        self.has_taken_paid_action = True
        self.log_action("Build Palace", "-30 Grain, -25 Timber, -15 Bronze | +3 Prestige/turn")
        self.add_message("✓ Palace built! +3 Prestige per turn.", "success")
        self.check_and_auto_end_turn()
        return True

    def build_lighthouse(self):
        if self.has_taken_paid_action:
            self.add_message("❌ You've already taken your paid action this turn!", "danger")
            return False
        if self.has_lighthouse:
            self.add_message("Lighthouse already built!", "warning")
            return False
        if self.grain < 20 or self.timber < 20:
            self.add_message("Insufficient resources! Need 20 Grain, 20 Timber.", "danger")
            return False

        self.grain -= 20
        self.timber -= 20
        self.has_lighthouse = True
        self.has_taken_paid_action = True
        self.log_action("Build Lighthouse", "-20 Grain, -20 Timber | +2 Prestige/turn, -1 Collapse/turn")
        self.add_message("✓ Lighthouse built! +2 Prestige per turn, -1 Collapse per turn.", "success")
        self.check_and_auto_end_turn()
        return True

    def build_watchtower(self):
        if self.has_taken_paid_action:
            self.add_message("❌ You've already taken your paid action this turn!", "danger")
            return False
        if self.has_watchtower:
            self.add_message("Watchtower already built!", "warning")
            return False
        if self.grain < 15 or self.timber < 15:
            self.add_message("Insufficient resources! Need 15 Grain, 15 Timber.", "danger")
            return False

        self.grain -= 15
        self.timber -= 15
        self.has_watchtower = True
        self.has_taken_paid_action = True
        self.log_action("Build Watchtower", "-15 Grain, -15 Timber | +1 Military/turn")
        self.add_message("✓ Watchtower built! +1 Military per turn.", "success")
        self.check_and_auto_end_turn()
        return True

    # Research actions
    def research_imperial_bureaucracy(self):
        if self.has_taken_paid_action:
            self.add_message("❌ You've already taken your paid action this turn!", "danger")
            return False
        if self.has_imperial_bureaucracy:
            self.add_message("Already researched!", "warning")
            return False
        if self.grain < 20 or self.prestige < 20:
            self.add_message("Insufficient resources! Need 20 Grain, 20 Prestige.", "danger")
            return False

        self.grain -= 20
        self.prestige -= 20
        self.has_imperial_bureaucracy = True
        self.has_taken_paid_action = True
        self.log_action("Research Imperial Bureaucracy", "-20 Grain, -20 Prestige | Reduces stability drift")
        self.add_message("✓ Imperial Bureaucracy researched! Stability drift reduced.", "success")
        self.check_and_auto_end_turn()
        return True

    def research_tin_trade_routes(self):
        if self.has_taken_paid_action:
            self.add_message("❌ You've already taken your paid action this turn!", "danger")
            return False
        if self.has_tin_trade_routes:
            self.add_message("Already researched!", "warning")
            return False
        if self.grain < 25 or self.bronze < 15:
            self.add_message("Insufficient resources! Need 25 Grain, 15 Bronze.", "danger")
            return False

        self.grain -= 25
        self.bronze -= 15
        self.has_tin_trade_routes = True
        self.has_taken_paid_action = True
        self.log_action("Research Tin Trade Routes", "-25 Grain, -15 Bronze | +1 Bronze/turn")
        self.add_message("✓ Tin Trade Routes researched! +1 Bronze per turn.", "success")
        self.check_and_auto_end_turn()
        return True

    def research_phalanx_formation(self):
        if self.has_taken_paid_action:
            self.add_message("❌ You've already taken your paid action this turn!", "danger")
            return False
        if self.has_phalanx_formation:
            self.add_message("Already researched!", "warning")
            return False
        if self.bronze < 20 or self.military < 25:
            self.add_message("Insufficient resources! Need 20 Bronze, 25 Military.", "danger")
            return False

        self.bronze -= 20
        self.military -= 25
        self.has_phalanx_formation = True
        self.has_taken_paid_action = True
        self.log_action("Research Phalanx Formation", "-20 Bronze, -25 Military | +2 Military/turn")
        self.add_message("✓ Phalanx Formation researched! +2 Military per turn.", "success")
        self.check_and_auto_end_turn()
        return True

    def research_diplomatic_marriage(self):
        if self.has_taken_paid_action:
            self.add_message("❌ You've already taken your paid action this turn!", "danger")
            return False
        if self.has_diplomatic_marriage:
            self.add_message("Already researched!", "warning")
            return False
        if self.prestige < 30:
            self.add_message("Insufficient Prestige! Need 30 Prestige.", "danger")
            return False

        self.prestige -= 30
        self.has_diplomatic_marriage = True
        self.has_taken_paid_action = True
        self.log_action("Research Diplomatic Marriage", "-30 Prestige | +1 Prestige/turn, -1 Collapse/turn")
        self.add_message("✓ Diplomatic Marriage researched! +1 Prestige per turn, -1 Collapse per turn.", "success")
        self.check_and_auto_end_turn()
        return True

    # Diplomacy actions
    def send_tribute(self, target="egypt"):
        if self.has_taken_paid_action:
            self.add_message("❌ You've already taken your paid action this turn!", "danger")
            return False
        if self.grain < 15 or self.bronze < 10:
            self.add_message("Insufficient resources! Need 15 Grain, 10 Bronze.", "danger")
            return False

        # Target-specific flavor text
        target_names = {
            "egypt": "🏛️ Egypt",
            "hittites": "⚔️ the Hittites",
            "assyria": "🦁 Assyria",
            "mycenae": "🏺 Mycenae"
        }
        target_name = target_names.get(target, "a great power")

        self.grain -= 15
        self.bronze -= 10
        self.prestige += 5
        self.collapse -= 3
        self.has_taken_paid_action = True
        self.log_action(f"Send Tribute to {target_name}", "-15 Grain, -10 Bronze | +5 Prestige, -3 Collapse")
        self.add_message(f"✓ Tribute sent to {target_name}: +5 Prestige, -3 Collapse", "success")
        self.check_and_auto_end_turn()
        return True

    def form_alliance(self):
        if self.has_taken_paid_action:
            self.add_message("❌ You've already taken your paid action this turn!", "danger")
            return False
        if self.prestige < 15:
            self.add_message("Insufficient Prestige! Need 15 Prestige.", "danger")
            return False

        self.prestige -= 15
        self.military += 5
        self.collapse -= 2
        self.has_taken_paid_action = True
        self.log_action("Form Alliance", "-15 Prestige | +5 Military, -2 Collapse")
        self.add_message("✓ Alliance formed: +5 Military, -2 Collapse", "success")
        self.check_and_auto_end_turn()
        return True

    def host_festival(self):
        if self.has_taken_paid_action:
            self.add_message("❌ You've already taken your paid action this turn!", "danger")
            return False
        if self.grain < 20:
            self.add_message("Insufficient Grain! Need 20 Grain.", "danger")
            return False

        self.grain -= 20
        self.stability += 10
        self.prestige += 3
        self.has_taken_paid_action = True
        self.log_action("Host Festival", "-20 Grain | +10 Stability, +3 Prestige")
        self.add_message("✓ Festival hosted: +10 Stability, +3 Prestige", "success")
        self.check_and_auto_end_turn()
        return True

    # Withdraw action
    def withdraw_from_alliance(self):
        if self.has_taken_paid_action:
            self.add_message("❌ You've already taken your paid action this turn!", "danger")
            return False
        if self.stability < 45:
            self.add_message("Cannot withdraw! Stability too low (need ≥45).", "danger")
            return False

        self.military += 10
        self.stability -= 15
        self.prestige -= 10
        self.collapse += 5
        self.has_taken_paid_action = True
        self.log_action("Withdraw from Alliance", "+10 Military, -15 Stability, -10 Prestige, +5 Collapse")
        self.add_message("✓ Withdrew from alliance: +10 Military, -15 Stability, -10 Prestige, +5 Collapse", "warning")
        self.check_and_auto_end_turn()
        return True

    # End-of-turn logic
    def end_turn(self):
        """Process end-of-turn effects and compile turn summary"""
        # Build turn summary
        summary = {
            'turn_number': self.turn,
            'actions': list(self.current_turn_actions),  # Copy actions taken
            'events': [],
            'income': [],
            'drift': []
        }

        # Per-turn yields from buildings
        if self.has_bronze_mine:
            self.bronze += 2
            summary['income'].append("Bronze Mine: +2 Bronze")
        if self.has_granary:
            self.grain += 3
            summary['income'].append("Granary: +3 Grain")
        if self.has_barracks:
            self.military += 2
            summary['income'].append("Barracks: +2 Military")
        if self.has_palace:
            self.prestige += 3
            summary['income'].append("Palace: +3 Prestige")
        if self.has_lighthouse:
            self.prestige += 2
            self.collapse -= 1
            summary['income'].append("Lighthouse: +2 Prestige, -1 Collapse")
        if self.has_watchtower:
            self.military += 1
            summary['income'].append("Watchtower: +1 Military")

        # Per-turn yields from techs
        if self.has_tin_trade_routes:
            self.bronze += 1
            summary['income'].append("Tin Trade Routes: +1 Bronze")
        if self.has_phalanx_formation:
            self.military += 2
            summary['income'].append("Phalanx Formation: +2 Military")
        if self.has_diplomatic_marriage:
            self.prestige += 1
            self.collapse -= 1
            summary['income'].append("Diplomatic Marriage: +1 Prestige, -1 Collapse")

        # Drift calculations
        stability_drift = -2
        if self.has_imperial_bureaucracy:
            stability_drift = -1
        self.stability += stability_drift
        summary['drift'].append(f"Stability: {stability_drift:+d}")

        collapse_drift = 1
        self.collapse += collapse_drift
        summary['drift'].append(f"Collapse: {collapse_drift:+d}")

        # Random events (stores in summary['events'])
        self.trigger_random_event_for_summary(summary)

        # Clamp values
        self.grain = max(0, self.grain)
        self.timber = max(0, self.timber)
        self.bronze = max(0, self.bronze)
        self.military = max(0, min(100, self.military))
        self.stability = max(0, min(100, self.stability))
        self.prestige = max(0, min(100, self.prestige))
        self.collapse = max(0, min(100, self.collapse))

        # Store summary and advance turn
        self.previous_turn_summary = summary
        self.turn_history.append(summary)
        self.current_turn_actions = []  # Clear for next turn

        # Reset turn action tracking (v2.3)
        self.has_used_free_harvest = False
        self.has_taken_paid_action = False

        self.turn += 1

        # Check win/loss conditions
        self.check_victory()

    def trigger_random_event_for_summary(self, summary):
        """Trigger a random event with 40% chance and add to summary"""
        if random.random() > 0.4:
            return

        events = [
            # Positive events (60%)
            {"name": "Bountiful Harvest", "grain": 10, "stability": 5, "collapse": -2, "weight": 15},
            {"name": "Trade Caravan Arrives", "bronze": 8, "prestige": 3, "collapse": -1, "weight": 12},
            {"name": "Diplomatic Victory", "prestige": 8, "collapse": -3, "weight": 10},
            {"name": "Military Recruitment", "military": 8, "grain": -5, "weight": 8},
            {"name": "Cultural Renaissance", "prestige": 10, "stability": 5, "weight": 8},
            {"name": "Improved Irrigation", "grain": 12, "collapse": -2, "weight": 7},

            # Negative events (40%)
            {"name": "Earthquake", "timber": -8, "stability": -5, "collapse": 3, "weight": 8},
            {"name": "Pirate Raid", "bronze": -6, "military": -3, "collapse": 2, "weight": 8},
            {"name": "Drought", "grain": -10, "stability": -5, "collapse": 2, "weight": 8},
            {"name": "Rebellion", "stability": -10, "military": -5, "collapse": 4, "weight": 7},
            {"name": "Trade Disruption", "bronze": -8, "prestige": -5, "collapse": 3, "weight": 6}
        ]

        # Weighted random selection
        total_weight = sum(e["weight"] for e in events)
        rand = random.uniform(0, total_weight)
        cumulative = 0

        for event in events:
            cumulative += event["weight"]
            if rand <= cumulative:
                self.apply_event_for_summary(event, summary)
                break

    def apply_event_for_summary(self, event, summary):
        """Apply event effects and record in summary"""
        effects = []

        if "grain" in event:
            self.grain += event["grain"]
            effects.append(f"{event['grain']:+d} Grain")
        if "timber" in event:
            self.timber += event["timber"]
            effects.append(f"{event['timber']:+d} Timber")
        if "bronze" in event:
            self.bronze += event["bronze"]
            effects.append(f"{event['bronze']:+d} Bronze")
        if "military" in event:
            self.military += event["military"]
            effects.append(f"{event['military']:+d} Military")
        if "stability" in event:
            self.stability += event["stability"]
            effects.append(f"{event['stability']:+d} Stability")
        if "prestige" in event:
            self.prestige += event["prestige"]
            effects.append(f"{event['prestige']:+d} Prestige")
        if "collapse" in event:
            self.collapse += event["collapse"]
            effects.append(f"{event['collapse']:+d} Collapse")

        # Add to summary
        event_description = f"{event['name']}: {', '.join(effects)}"
        summary['events'].append(event_description)

    def check_victory(self):
        """Check win/loss conditions"""
        # Loss conditions
        if self.stability <= 0:
            self.game_over = True
            self.victory_type = "loss_stability"
            return

        if self.collapse >= 100:
            self.game_over = True
            self.victory_type = "loss_collapse"
            return

        # Win conditions
        if self.collapse <= 0:
            self.game_over = True
            self.victory_type = "win_preservation"
            return

        if self.turn > self.max_turns:
            if self.collapse >= 80 and self.military >= 50:
                self.game_over = True
                self.victory_type = "win_vacuum"
            else:
                self.game_over = True
                self.victory_type = "loss_time"
