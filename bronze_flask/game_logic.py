"""
Core game logic for BRONZE: 1177 BC
Ported from v1.2.6 CLI version
"""

import random

class GameState:
    def __init__(self):
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
        self.max_turns = 20
        self.game_over = False
        self.victory_type = None
        self.message_log = []

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
            'max_turns': self.max_turns,
            'game_over': self.game_over,
            'victory_type': self.victory_type,
            'message_log': self.message_log
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

    # Actions
    def harvest(self):
        """Action: Harvest (+15 Grain, +10 Bronze)"""
        self.grain += 15
        self.bronze += 10
        self.add_message("Harvested: +15 Grain, +10 Bronze", "success")
        return True

    def gather_timber(self):
        """Action: Gather Timber (-8 Grain → +10 Timber)"""
        if self.grain < 8:
            self.add_message("Insufficient Grain! Need 8 Grain.", "danger")
            return False

        self.grain -= 8
        self.timber += 10
        self.add_message("Gathered Timber: -8 Grain, +10 Timber", "success")
        return True

    def fortify(self):
        """Action: Fortify (+5 Military, -5 Stability)"""
        self.military += 5
        self.stability -= 5
        self.add_message("Fortified: +5 Military, -5 Stability", "success")
        return True

    # Building actions
    def build_bronze_mine(self):
        if self.has_bronze_mine:
            self.add_message("Bronze Mine already built!", "warning")
            return False
        if self.grain < 15 or self.timber < 10:
            self.add_message("Insufficient resources! Need 15 Grain, 10 Timber.", "danger")
            return False

        self.grain -= 15
        self.timber -= 10
        self.has_bronze_mine = True
        self.add_message("Bronze Mine built! +2 Bronze per turn.", "success")
        return True

    def build_granary(self):
        if self.has_granary:
            self.add_message("Granary already built!", "warning")
            return False
        if self.grain < 20 or self.timber < 15:
            self.add_message("Insufficient resources! Need 20 Grain, 15 Timber.", "danger")
            return False

        self.grain -= 20
        self.timber -= 15
        self.has_granary = True
        self.add_message("Granary built! +3 Grain per turn.", "success")
        return True

    def build_barracks(self):
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
        self.add_message("Barracks built! +2 Military per turn.", "success")
        return True

    def build_palace(self):
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
        self.add_message("Palace built! +3 Prestige per turn.", "success")
        return True

    def build_lighthouse(self):
        if self.has_lighthouse:
            self.add_message("Lighthouse already built!", "warning")
            return False
        if self.grain < 20 or self.timber < 20:
            self.add_message("Insufficient resources! Need 20 Grain, 20 Timber.", "danger")
            return False

        self.grain -= 20
        self.timber -= 20
        self.has_lighthouse = True
        self.add_message("Lighthouse built! +2 Prestige per turn, -1 Collapse per turn.", "success")
        return True

    def build_watchtower(self):
        if self.has_watchtower:
            self.add_message("Watchtower already built!", "warning")
            return False
        if self.grain < 15 or self.timber < 15:
            self.add_message("Insufficient resources! Need 15 Grain, 15 Timber.", "danger")
            return False

        self.grain -= 15
        self.timber -= 15
        self.has_watchtower = True
        self.add_message("Watchtower built! +1 Military per turn.", "success")
        return True

    # Research actions
    def research_imperial_bureaucracy(self):
        if self.has_imperial_bureaucracy:
            self.add_message("Already researched!", "warning")
            return False
        if self.grain < 20 or self.prestige < 20:
            self.add_message("Insufficient resources! Need 20 Grain, 20 Prestige.", "danger")
            return False

        self.grain -= 20
        self.prestige -= 20
        self.has_imperial_bureaucracy = True
        self.add_message("Imperial Bureaucracy researched! Stability drift reduced.", "success")
        return True

    def research_tin_trade_routes(self):
        if self.has_tin_trade_routes:
            self.add_message("Already researched!", "warning")
            return False
        if self.grain < 25 or self.bronze < 15:
            self.add_message("Insufficient resources! Need 25 Grain, 15 Bronze.", "danger")
            return False

        self.grain -= 25
        self.bronze -= 15
        self.has_tin_trade_routes = True
        self.add_message("Tin Trade Routes researched! +1 Bronze per turn.", "success")
        return True

    def research_phalanx_formation(self):
        if self.has_phalanx_formation:
            self.add_message("Already researched!", "warning")
            return False
        if self.bronze < 20 or self.military < 25:
            self.add_message("Insufficient resources! Need 20 Bronze, 25 Military.", "danger")
            return False

        self.bronze -= 20
        self.military -= 25
        self.has_phalanx_formation = True
        self.add_message("Phalanx Formation researched! +2 Military per turn.", "success")
        return True

    def research_diplomatic_marriage(self):
        if self.has_diplomatic_marriage:
            self.add_message("Already researched!", "warning")
            return False
        if self.prestige < 30:
            self.add_message("Insufficient Prestige! Need 30 Prestige.", "danger")
            return False

        self.prestige -= 30
        self.has_diplomatic_marriage = True
        self.add_message("Diplomatic Marriage researched! +1 Prestige per turn, -1 Collapse per turn.", "success")
        return True

    # Diplomacy actions
    def send_tribute(self):
        if self.grain < 15 or self.bronze < 10:
            self.add_message("Insufficient resources! Need 15 Grain, 10 Bronze.", "danger")
            return False

        self.grain -= 15
        self.bronze -= 10
        self.prestige += 5
        self.collapse -= 3
        self.add_message("Tribute sent: +5 Prestige, -3 Collapse", "success")
        return True

    def form_alliance(self):
        if self.prestige < 15:
            self.add_message("Insufficient Prestige! Need 15 Prestige.", "danger")
            return False

        self.prestige -= 15
        self.military += 5
        self.collapse -= 2
        self.add_message("Alliance formed: +5 Military, -2 Collapse", "success")
        return True

    def host_festival(self):
        if self.grain < 20:
            self.add_message("Insufficient Grain! Need 20 Grain.", "danger")
            return False

        self.grain -= 20
        self.stability += 10
        self.prestige += 3
        self.add_message("Festival hosted: +10 Stability, +3 Prestige", "success")
        return True

    # Withdraw action
    def withdraw_from_alliance(self):
        if self.stability < 45:
            self.add_message("Cannot withdraw! Stability too low (need ≥45).", "danger")
            return False

        self.military += 10
        self.stability -= 15
        self.prestige -= 10
        self.collapse += 5
        self.add_message("Withdrew from alliance: +10 Military, -15 Stability, -10 Prestige, +5 Collapse", "warning")
        return True

    # End-of-turn logic
    def end_turn(self):
        """Process end-of-turn effects"""
        self.turn += 1

        # Per-turn yields from buildings
        if self.has_bronze_mine:
            self.bronze += 2
        if self.has_granary:
            self.grain += 3
        if self.has_barracks:
            self.military += 2
        if self.has_palace:
            self.prestige += 3
        if self.has_lighthouse:
            self.prestige += 2
            self.collapse -= 1
        if self.has_watchtower:
            self.military += 1

        # Per-turn yields from techs
        if self.has_tin_trade_routes:
            self.bronze += 1
        if self.has_phalanx_formation:
            self.military += 2
        if self.has_diplomatic_marriage:
            self.prestige += 1
            self.collapse -= 1

        # Drift calculations
        stability_drift = -2
        if self.has_imperial_bureaucracy:
            stability_drift = -1
        self.stability += stability_drift

        collapse_drift = 1
        self.collapse += collapse_drift

        # Random events
        self.trigger_random_event()

        # Clamp values
        self.grain = max(0, self.grain)
        self.timber = max(0, self.timber)
        self.bronze = max(0, self.bronze)
        self.military = max(0, min(100, self.military))
        self.stability = max(0, min(100, self.stability))
        self.prestige = max(0, min(100, self.prestige))
        self.collapse = max(0, min(100, self.collapse))

        # Check win/loss conditions
        self.check_victory()

    def trigger_random_event(self):
        """Trigger a random event with 40% chance"""
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
                self.apply_event(event)
                break

    def apply_event(self, event):
        """Apply event effects"""
        msg_parts = [f"EVENT: {event['name']}!"]
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

        msg_parts.append(" | ".join(effects))

        # Determine message type
        msg_type = "info"
        if event.get("collapse", 0) < 0:
            msg_type = "success"
        elif event.get("collapse", 0) > 0:
            msg_type = "warning"

        self.add_message(" - ".join(msg_parts), msg_type)

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
