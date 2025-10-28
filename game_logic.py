# game_logic.py
# BRONZE: 1177 BC — Flask build (v4.1 parity patch)
# - Restores rich event pool & weights (v1.2 feel)
# - Turn summary logging for UI
# - FREE Harvest + exactly ONE paid action per turn
# - No turn advance on cancel/insufficient resources
# - Imperial Bureaucracy mitigates Stability losses (-25%)

from __future__ import annotations
from dataclasses import dataclass, field
import random
import logging
import math
from typing import Dict, List, Optional

# Configure logging
logger = logging.getLogger(__name__)


def clamp(v: int, lo: int = 0, hi: int = 100) -> int:
    return max(lo, min(hi, v))


@dataclass
class TurnSummary:
    turn_number: int
    actions: List[Dict[str, str]] = field(default_factory=list)
    events: List[str] = field(default_factory=list)
    income: List[str] = field(default_factory=list)
    drift: List[str] = field(default_factory=list)


@dataclass
class ChoiceEvent:
    """Represents a choice-based event that requires player decision"""
    event_id: str
    title: str
    description: str
    choice_a_label: str
    choice_a_effects: str
    choice_b_label: str
    choice_b_effects: str


@dataclass
class Game:
    # Core resources / metrics
    grain: int = 50
    bronze: int = 30
    timber: int = 20
    prestige: int = 10  # (luxuries in the CLI build — named 'prestige' here)
    stability: int = 65
    knowledge: int = 40
    elasticity: int = 50
    military: int = 30
    collapse: int = 45

    # Progress
    turn: int = 1
    max_turns: int = 20
    drift_per_turn: int = 3
    difficulty: str = "normal"  # Track difficulty level

    # Tech/build flags (simple booleans so UI can reflect state)
    tech_imperial_bureaucracy: bool = False
    tech_bronze_mines: bool = False
    tech_granary_network: bool = False
    tech_alphabetic_script: bool = False
    tech_ironworking: bool = False
    tech_diplomatic_protocols: bool = False
    tech_tin_trade_routes: bool = False
    tech_phalanx_formation: bool = False
    tech_diplomatic_marriage: bool = False

    # Build flags
    has_granary: bool = False
    has_library: bool = False
    has_walls: bool = False
    has_bronze_mine: bool = False
    has_barracks: bool = False
    has_palace: bool = False
    has_lighthouse: bool = False
    has_watchtower: bool = False

    # Per-turn economy: FREE harvest + ONE paid action
    free_harvest_used: bool = False
    paid_action_used: bool = False

    # Withdraw (vacuum push)
    withdrawals_used: int = 0
    max_withdrawals: int = 3

    # Messaging for UI
    message_log: List[Dict[str, str]] = field(default_factory=list)
    previous_turn_summary: Optional[TurnSummary] = None
    current_turn_actions: List[Dict[str, str]] = field(default_factory=list)

    # Choice events
    pending_choice: Optional[ChoiceEvent] = None
    
    def __post_init__(self):
        """Validate game state after initialization"""
        try:
            logger.info("Initializing new Game instance")
            # Validate initial state (using object.__setattr__ for dataclass fields)
            if self.turn < 1:
                logger.warning("Turn was less than 1, resetting to 1")
                object.__setattr__(self, 'turn', 1)
            if self.max_turns < 1:
                logger.warning("max_turns was less than 1, resetting to 20")
                object.__setattr__(self, 'max_turns', 20)
            # Initialize turn summary at game start
            self._start_turn_summary()
            logger.info(f"Game initialized: turn {self.turn}/{self.max_turns}")
        except Exception as e:
            logger.error(f"Error in Game.__post_init__: {e}", exc_info=True)

    # ------------------------
    # Utility / logging
    # ------------------------
    def _log(self, text: str, level: str = "info") -> None:
        """Add a message to the game log"""
        try:
            self.message_log.append({"type": level, "text": text})
            logger.debug(f"Game log [{level}]: {text}")
        except Exception as e:
            logger.error(f"Error in _log: {e}", exc_info=True)

    def _start_turn_summary(self) -> None:
        self.previous_turn_summary = TurnSummary(turn_number=self.turn)

    def _add_action_summary(self, name: str, effects: str) -> None:
        """Add an action to the turn summary with name and effects"""
        if not self.previous_turn_summary or self.previous_turn_summary.turn_number != self.turn:
            self._start_turn_summary()
        self.previous_turn_summary.actions.append({"name": name, "effects": effects})
    
    def _add_current_turn_action(self, name: str, effects: str) -> None:
        """Add an action to the current turn tracking"""
        self.current_turn_actions.append({"name": name, "effects": effects})

    def _add_event_summary(self, line: str) -> None:
        if not self.previous_turn_summary or self.previous_turn_summary.turn_number != self.turn:
            self._start_turn_summary()
        self.previous_turn_summary.events.append(line)

    def _add_income_summary(self, line: str) -> None:
        if not self.previous_turn_summary or self.previous_turn_summary.turn_number != self.turn:
            self._start_turn_summary()
        self.previous_turn_summary.income.append(line)

    def _add_drift_summary(self, line: str) -> None:
        if not self.previous_turn_summary or self.previous_turn_summary.turn_number != self.turn:
            self._start_turn_summary()
        self.previous_turn_summary.drift.append(line)

    # Safe stat application (with IB mitigation)
    def _apply(self,
               d_grain: int = 0, d_bronze: int = 0, d_timber: int = 0, d_prestige: int = 0,
               d_stab: int = 0, d_know: int = 0, d_elast: int = 0, d_mil: int = 0, d_col: int = 0) -> str:

        if self.tech_imperial_bureaucracy and d_stab < 0:
            # Apply 25% reduction, then ceil rounds negative values up (e.g., -7.5 → -7, -10 → -10)
            d_stab = math.ceil(d_stab * 0.75)

        self.grain += d_grain
        self.bronze += d_bronze
        self.timber += d_timber
        self.prestige += d_prestige
        self.stability = clamp(self.stability + d_stab)
        self.knowledge = clamp(self.knowledge + d_know)
        self.elasticity = clamp(self.elasticity + d_elast)
        self.military = clamp(self.military + d_mil)
        self.collapse = clamp(self.collapse + d_col)

        parts: List[str] = []
        if d_grain: parts.append(f"Grain {d_grain:+}")
        if d_bronze: parts.append(f"Bronze {d_bronze:+}")
        if d_timber: parts.append(f"Timber {d_timber:+}")
        if d_prestige: parts.append(f"Luxuries {d_prestige:+}")
        if d_stab: parts.append(f"Stability {d_stab:+}")
        if d_know: parts.append(f"Knowledge {d_know:+}")
        if d_elast: parts.append(f"Elasticity {d_elast:+}")
        if d_mil: parts.append(f"Military {d_mil:+}")
        if d_col: parts.append(f"Collapse {d_col:+}")
        return ", ".join(parts) if parts else "—"

    # ------------------------
    # Actions (return bool for “performed” so caller won’t advance turn on False)
    # ------------------------
    def harvest_free(self) -> bool:
        if self.free_harvest_used:
            self._log("You already took the free Harvest this turn.", "warning")
            return False
        detail = self._apply(d_grain=+15, d_bronze=+10)
        self._add_action_summary("Harvest", detail)
        self._add_current_turn_action("Harvest", "+15 Grain, +10 Bronze")
        self.free_harvest_used = True
        self._log("✓ Harvested! +15 Grain, +10 Bronze", "success")
        return True

    def gather_timber(self) -> bool:
        # Paid action
        if self.paid_action_used:
            self._log("You already used your paid action this turn.", "warning")
            return False
        if self.grain < 8:
            self._log("✗ Not enough Grain (need 8) to Gather Timber.", "danger")
            return False
        detail = self._apply(d_grain=-8, d_timber=+10)
        self._add_action_summary("Gather Timber", detail)
        self._add_current_turn_action("Gather Timber", "-8 Grain, +10 Timber")
        self.paid_action_used = True
        self._log("✓ Gathered Timber! -8 Grain, +10 Timber", "success")
        return True

    def fortify(self) -> bool:
        if self.paid_action_used:
            self._log("You already used your paid action this turn.", "warning")
            return False
        if self.bronze < 10:
            self._log("✗ Not enough Bronze (need 10) to Fortify.", "danger")
            return False
        detail = self._apply(d_bronze=-10, d_mil=+8)
        self._add_action_summary("Fortify Defenses", detail)
        self._add_current_turn_action("Fortify Defenses", "-10 Bronze, +8 Military")
        self.paid_action_used = True
        self._log("✓ Defenses fortified! -10 Bronze, +8 Military", "success")
        return True

    def withdraw_support(self) -> bool:
        if self.paid_action_used:
            self._log("You already used your paid action this turn.", "warning")
            return False
        if self.withdrawals_used >= self.max_withdrawals:
            self._log("✗ No withdrawals remaining.", "danger")
            return False
        if self.stability < 45:
            self._log("✗ Withdraw locked — requires Stability ≥ 45.", "warning")
            return False
        detail = self._apply(d_stab=-10, d_col=+15)
        self.withdrawals_used += 1
        self._add_action_summary("Withdraw Support", detail)
        self._add_current_turn_action("Withdraw Support", "-10 Stability, +15 Collapse")
        self.paid_action_used = True
        self._log(f"⚠️ Support withdrawn ({self.max_withdrawals - self.withdrawals_used} left). +15 Collapse, -10 Stability", "danger")
        return True

    # Minimal tech/build hooks (keep names your UI expects)
    def research_imperial_bureaucracy(self) -> bool:
        if self.paid_action_used:
            self._log("You already used your paid action this turn.", "warning")
            return False
        # Example cost: 15 Knowledge, 20 Grain
        if self.knowledge < 15 or self.grain < 20:
            self._log("✗ Insufficient resources for Imperial Bureaucracy.", "danger")
            return False
        detail = self._apply(d_know=-15, d_grain=-20, d_elast=+10)
        self.tech_imperial_bureaucracy = True
        self._add_action_summary("Researched Imperial Bureaucracy", detail)
        self._add_current_turn_action("Researched Imperial Bureaucracy", "-15 Knowledge, -20 Grain, +10 Elasticity")
        self.paid_action_used = True
        self._log("✓ Researched Imperial Bureaucracy! Stability losses reduced 25%.", "success")
        return True

    def build_bronze_mine(self) -> bool:
        if self.paid_action_used:
            self._log("You already used your paid action this turn.", "warning")
            return False
        if self.timber < 20 or self.grain < 15:
            self._log("✗ Not enough Timber (20) and Grain (15) to build Bronze Mine.", "danger")
            return False
        detail = self._apply(d_timber=-20, d_grain=-15)
        self.has_bronze_mine = True
        self._add_action_summary("Built Bronze Mine", f"{detail} → +3 Bronze/turn")
        self._add_current_turn_action("Built Bronze Mine", "-20 Timber, -15 Grain → +3 Bronze/turn")
        self.paid_action_used = True
        self._log("✓ Bronze Mine built! +3 Bronze each turn.", "success")
        return True

    def build_granary(self) -> bool:
        if self.paid_action_used:
            self._log("You already used your paid action this turn.", "warning")
            return False
        if self.has_granary:
            self._log("✗ Granary already built.", "warning")
            return False
        if self.timber < 15 or self.grain < 20:
            self._log("✗ Not enough Timber (15) and Grain (20) to build Granary.", "danger")
            return False
        detail = self._apply(d_timber=-15, d_grain=-20)
        self.has_granary = True
        self._add_action_summary("Built Granary", f"{detail} → +5 Grain/turn")
        self._add_current_turn_action("Built Granary", "-15 Timber, -20 Grain → +5 Grain/turn")
        self.paid_action_used = True
        self._log("✓ Granary built! +5 Grain each turn.", "success")
        return True

    def build_barracks(self) -> bool:
        if self.paid_action_used:
            self._log("You already used your paid action this turn.", "warning")
            return False
        if self.has_barracks:
            self._log("✗ Barracks already built.", "warning")
            return False
        if self.timber < 20 or self.grain < 25 or self.bronze < 10:
            self._log("✗ Not enough Timber (20), Grain (25), and Bronze (10) to build Barracks.", "danger")
            return False
        detail = self._apply(d_timber=-20, d_grain=-25, d_bronze=-10, d_mil=+15)
        self.has_barracks = True
        self._add_action_summary("Built Barracks", detail)
        self._add_current_turn_action("Built Barracks", "-20 Timber, -25 Grain, -10 Bronze, +15 Military")
        self.paid_action_used = True
        self._log("✓ Barracks built! +15 Military.", "success")
        return True

    def build_palace(self) -> bool:
        if self.paid_action_used:
            self._log("You already used your paid action this turn.", "warning")
            return False
        if self.has_palace:
            self._log("✗ Palace already built.", "warning")
            return False
        if self.timber < 25 or self.grain < 30 or self.bronze < 15:
            self._log("✗ Not enough Timber (25), Grain (30), and Bronze (15) to build Palace.", "danger")
            return False
        detail = self._apply(d_timber=-25, d_grain=-30, d_bronze=-15, d_prestige=+20, d_stab=+10)
        self.has_palace = True
        self._add_action_summary("Built Palace", detail)
        self._add_current_turn_action("Built Palace", "-25 Timber, -30 Grain, -15 Bronze, +20 Prestige, +10 Stability")
        self.paid_action_used = True
        self._log("✓ Palace built! +20 Prestige, +10 Stability.", "success")
        return True

    def build_lighthouse(self) -> bool:
        if self.paid_action_used:
            self._log("You already used your paid action this turn.", "warning")
            return False
        if self.has_lighthouse:
            self._log("✗ Lighthouse already built.", "warning")
            return False
        if self.timber < 20 or self.grain < 20:
            self._log("✗ Not enough Timber (20) and Grain (20) to build Lighthouse.", "danger")
            return False
        detail = self._apply(d_timber=-20, d_grain=-20, d_prestige=+10, d_col=-3)
        self.has_lighthouse = True
        self._add_action_summary("Built Lighthouse", detail)
        self._add_current_turn_action("Built Lighthouse", "-20 Timber, -20 Grain, +10 Prestige, -3 Collapse")
        self.paid_action_used = True
        self._log("✓ Lighthouse built! +10 Prestige, -3 Collapse.", "success")
        return True

    def build_watchtower(self) -> bool:
        if self.paid_action_used:
            self._log("You already used your paid action this turn.", "warning")
            return False
        if self.has_watchtower:
            self._log("✗ Watchtower already built.", "warning")
            return False
        if self.timber < 15 or self.grain < 15:
            self._log("✗ Not enough Timber (15) and Grain (15) to build Watchtower.", "danger")
            return False
        detail = self._apply(d_timber=-15, d_grain=-15, d_mil=+10)
        self.has_watchtower = True
        self._add_action_summary("Built Watchtower", detail)
        self._add_current_turn_action("Built Watchtower", "-15 Timber, -15 Grain, +10 Military")
        self.paid_action_used = True
        self._log("✓ Watchtower built! +10 Military.", "success")
        return True

    def research_tin_trade_routes(self) -> bool:
        if self.paid_action_used:
            self._log("You already used your paid action this turn.", "warning")
            return False
        if self.tech_tin_trade_routes:
            self._log("✗ Tin Trade Routes already researched.", "warning")
            return False
        if self.grain < 25 or self.bronze < 15:
            self._log("✗ Not enough Grain (25) and Bronze (15) for Tin Trade Routes.", "danger")
            return False
        detail = self._apply(d_grain=-25, d_bronze=-15, d_prestige=+10, d_col=-2)
        self.tech_tin_trade_routes = True
        self._add_action_summary("Researched Tin Trade Routes", detail)
        self._add_current_turn_action("Researched Tin Trade Routes", "-25 Grain, -15 Bronze, +10 Prestige, -2 Collapse")
        self.paid_action_used = True
        self._log("✓ Researched Tin Trade Routes! +10 Prestige, -2 Collapse.", "success")
        return True

    def research_phalanx_formation(self) -> bool:
        if self.paid_action_used:
            self._log("You already used your paid action this turn.", "warning")
            return False
        if self.tech_phalanx_formation:
            self._log("✗ Phalanx Formation already researched.", "warning")
            return False
        if self.bronze < 20 or self.military < 25:
            self._log("✗ Not enough Bronze (20) and Military (25) for Phalanx Formation.", "danger")
            return False
        detail = self._apply(d_bronze=-20, d_mil=+15)
        self.tech_phalanx_formation = True
        self._add_action_summary("Researched Phalanx Formation", detail)
        self._add_current_turn_action("Researched Phalanx Formation", "-20 Bronze, +15 Military")
        self.paid_action_used = True
        self._log("✓ Researched Phalanx Formation! +15 Military.", "success")
        return True

    def research_diplomatic_marriage(self) -> bool:
        if self.paid_action_used:
            self._log("You already used your paid action this turn.", "warning")
            return False
        if self.tech_diplomatic_marriage:
            self._log("✗ Diplomatic Marriage already researched.", "warning")
            return False
        if self.prestige < 30:
            self._log("✗ Not enough Prestige (30) for Diplomatic Marriage.", "danger")
            return False
        detail = self._apply(d_prestige=-30, d_stab=+15, d_col=-5)
        self.tech_diplomatic_marriage = True
        self._add_action_summary("Researched Diplomatic Marriage", detail)
        self._add_current_turn_action("Researched Diplomatic Marriage", "-30 Prestige, +15 Stability, -5 Collapse")
        self.paid_action_used = True
        self._log("✓ Researched Diplomatic Marriage! +15 Stability, -5 Collapse.", "success")
        return True

    def send_tribute(self, target: str) -> bool:
        if self.paid_action_used:
            self._log("You already used your paid action this turn.", "warning")
            return False
        if self.grain < 15 or self.bronze < 10:
            self._log("✗ Not enough Grain (15) and Bronze (10) to send tribute.", "danger")
            return False
        detail = self._apply(d_grain=-15, d_bronze=-10, d_prestige=+5, d_col=-3)
        self._add_action_summary(f"Sent tribute to {target.capitalize()}", detail)
        self._add_current_turn_action(f"Sent tribute to {target.capitalize()}", "-15 Grain, -10 Bronze, +5 Prestige, -3 Collapse")
        self.paid_action_used = True
        self._log(f"✓ Tribute sent to {target.capitalize()}! +5 Prestige, -3 Collapse.", "success")
        return True

    def form_alliance(self) -> bool:
        if self.paid_action_used:
            self._log("You already used your paid action this turn.", "warning")
            return False
        if self.prestige < 15:
            self._log("✗ Not enough Prestige (15) to form alliance.", "danger")
            return False
        detail = self._apply(d_prestige=-15, d_stab=+8, d_mil=+5, d_col=-4)
        self._add_action_summary("Formed Alliance", detail)
        self._add_current_turn_action("Formed Alliance", "-15 Prestige, +8 Stability, +5 Military, -4 Collapse")
        self.paid_action_used = True
        self._log("✓ Alliance formed! +8 Stability, +5 Military, -4 Collapse.", "success")
        return True

    def host_festival(self) -> bool:
        if self.paid_action_used:
            self._log("You already used your paid action this turn.", "warning")
            return False
        if self.grain < 20:
            self._log("✗ Not enough Grain (20) to host festival.", "danger")
            return False
        detail = self._apply(d_grain=-20, d_stab=+10, d_prestige=+8)
        self._add_action_summary("Hosted Festival", detail)
        self._add_current_turn_action("Hosted Festival", "-20 Grain, +10 Stability, +8 Prestige")
        self.paid_action_used = True
        self._log("✓ Festival hosted! +10 Stability, +8 Prestige.", "success")
        return True

    # ------------------------
    # End-of-turn / economy / events
    # ------------------------
    def apply_income(self) -> None:
        if self.has_bronze_mine:
            self.bronze += 3
            self._add_income_summary("Bronze Mines: +3 Bronze")
        if self.has_granary or self.tech_granary_network:
            self.grain += 5
            self._add_income_summary("Granary Network: +5 Grain")

    def apply_drift(self) -> None:
        self.collapse = clamp(self.collapse + self.drift_per_turn)
        self._add_drift_summary(f"Collapse Drift: +{self.drift_per_turn}")

    # Event tables (v1.2 feel)
    def resolve_random_event(self) -> None:
        NEG, POS, CHOICE = "neg", "pos", "choice"
        tables = {
            NEG: [
                ("Sea Peoples Raid",        6,  lambda: self._apply(d_mil=-12, d_stab=-9,  d_col=+8)),
                ("Trade Route Disruption",  5,  lambda: self._apply(d_bronze=-10, d_prestige=-5, d_stab=-6, d_col=+6)),
                ("Palace Conspiracy",       4,  lambda: self._apply(d_stab=-15, d_prestige=-8, d_col=+5)),
                ("Drought in Anatolia",     4,  lambda: self._apply(d_grain=-15, d_stab=-7,  d_col=+5)),
                ("Vassal Rebellion",        3,  lambda: self._apply(d_mil=-10, d_stab=-11, d_grain=-10, d_col=+7)),
            ],
            POS: [
                ("Diplomatic Success",      6,  lambda: self._apply(d_stab=+12, d_prestige=+8, d_col=-4)),
                ("Bountiful Harvest",       5,  lambda: self._apply(d_grain=+20, d_stab=+8,  d_col=-3)),
                ("Military Victory",        4,  lambda: self._apply(d_mil=+12, d_stab=+10,  d_col=-3)),
                ("Technological Breakthrough", 3, lambda: self._apply(d_know=+15, d_stab=+5, d_col=-2)),
            ],
        }
        NEGATIVE_CHANCE = 0.50
        POSITIVE_CHANCE = 0.30
        CHOICE_CHANCE = 0.10

        r = random.random()
        if r < NEGATIVE_CHANCE:
            name, delta = self._weighted_apply(tables[NEG])
            self._log(f"✗ CRISIS: {name} — {delta}", "danger")
            self._add_event_summary(f"CRISIS: {name} — {delta}")
        elif r < NEGATIVE_CHANCE + POSITIVE_CHANCE:
            name, delta = self._weighted_apply(tables[POS])
            self._log(f"✓ POSITIVE EVENT: {name} — {delta}", "success")
            self._add_event_summary(f"POSITIVE: {name} — {delta}")
        elif r < NEGATIVE_CHANCE + POSITIVE_CHANCE + CHOICE_CHANCE:
            # Trigger a choice event
            self._trigger_choice_event()
        else:
            # No event
            pass

    def _weighted_apply(self, table):
        total = sum(w for _, w, _ in table)
        pick = random.uniform(0, total)
        upto = 0
        for name, w, fn in table:
            if upto + w >= pick:
                delta = fn()
                return name, (delta or "—")
            upto += w
        name, _, fn = table[-1]
        delta = fn()
        return name, (delta or "—")

    def _trigger_choice_event(self) -> None:
        """Randomly select and trigger a choice event"""
        choice_events = [
            self._create_vassal_aid_choice,
            self._create_hittite_trade_choice,
            self._create_refugee_crisis_choice,
        ]
        choice_fn = random.choice(choice_events)
        self.pending_choice = choice_fn()
        self._log(f"⚠️ CHOICE EVENT: {self.pending_choice.title}", "warning")

    def _create_vassal_aid_choice(self) -> ChoiceEvent:
        """Vassal Requests Aid choice event"""
        return ChoiceEvent(
            event_id="vassal_aid",
            title="Vassal Requests Aid",
            description="A vassal kingdom sends urgent word: famine threatens their lands. They request grain supplies to stabilize their region.",
            choice_a_label="Send Grain (-20 Grain)",
            choice_a_effects="+8 Prestige, +5 Stability, -2 Collapse",
            choice_b_label="Refuse Aid",
            choice_b_effects="-10 Prestige, -8 Stability, +3 Collapse"
        )

    def _create_hittite_trade_choice(self) -> ChoiceEvent:
        """Hittite Trade Offer choice event"""
        return ChoiceEvent(
            event_id="hittite_trade",
            title="Hittite Trade Offer",
            description="Hittite merchants arrive with a trade proposal: they offer valuable bronze ingots in exchange for timber from your forests.",
            choice_a_label="Accept Trade (-15 Timber)",
            choice_a_effects="+12 Bronze, +5 Prestige, -1 Collapse",
            choice_b_label="Decline Offer",
            choice_b_effects="-3 Prestige"
        )

    def _create_refugee_crisis_choice(self) -> ChoiceEvent:
        """Refugee Crisis choice event"""
        return ChoiceEvent(
            event_id="refugee_crisis",
            title="Refugee Crisis",
            description="Refugees from a collapsed neighboring kingdom arrive at your borders, seeking shelter and protection.",
            choice_a_label="Welcome Refugees (-12 Grain)",
            choice_a_effects="+10 Stability, +6 Military, -2 Collapse",
            choice_b_label="Turn Them Away",
            choice_b_effects="-12 Stability, +3 Military, +4 Collapse"
        )

    def resolve_choice(self, choice: str) -> bool:
        """Handle player's choice for a pending choice event"""
        try:
            if not self.pending_choice:
                logger.warning("resolve_choice called with no pending choice")
                return False

            event_id = self.pending_choice.event_id
            logger.info(f"Resolving choice event {event_id} with choice {choice}")
            
            if event_id == "vassal_aid":
                if choice == "a":
                    if self.grain < 20:
                        self._log("Insufficient Grain to send aid!", "danger")
                        return False
                    self.grain -= 20
                    self._apply(d_prestige=+8, d_stab=+5, d_col=-2)
                    self._log(f"✓ {self.pending_choice.choice_a_label}: {self.pending_choice.choice_a_effects}", "success")
                    self._add_event_summary(f"CHOICE: {self.pending_choice.title} → Sent Aid")
                else:
                    self._apply(d_prestige=-10, d_stab=-8, d_col=+3)
                    self._log(f"✓ {self.pending_choice.choice_b_label}: {self.pending_choice.choice_b_effects}", "warning")
                    self._add_event_summary(f"CHOICE: {self.pending_choice.title} → Refused")
            
            elif event_id == "hittite_trade":
                if choice == "a":
                    if self.timber < 15:
                        self._log("Insufficient Timber for trade!", "danger")
                        return False
                    self.timber -= 15
                    self._apply(d_bronze=+12, d_prestige=+5, d_col=-1)
                    self._log(f"✓ {self.pending_choice.choice_a_label}: {self.pending_choice.choice_a_effects}", "success")
                    self._add_event_summary(f"CHOICE: {self.pending_choice.title} → Accepted Trade")
                else:
                    self._apply(d_prestige=-3)
                    self._log(f"✓ {self.pending_choice.choice_b_label}: {self.pending_choice.choice_b_effects}", "warning")
                    self._add_event_summary(f"CHOICE: {self.pending_choice.title} → Declined")
            
            elif event_id == "refugee_crisis":
                if choice == "a":
                    if self.grain < 12:
                        self._log("Insufficient Grain to welcome refugees!", "danger")
                        return False
                    self.grain -= 12
                    self._apply(d_stab=+10, d_mil=+6, d_col=-2)
                    self._log(f"✓ {self.pending_choice.choice_a_label}: {self.pending_choice.choice_a_effects}", "success")
                    self._add_event_summary(f"CHOICE: {self.pending_choice.title} → Welcomed Refugees")
                else:
                    self._apply(d_stab=-12, d_mil=+3, d_col=+4)
                    self._log(f"✓ {self.pending_choice.choice_b_label}: {self.pending_choice.choice_b_effects}", "warning")
                    self._add_event_summary(f"CHOICE: {self.pending_choice.title} → Turned Away")
            
            self.pending_choice = None
            logger.info("Choice resolved successfully")
            return True
        except Exception as e:
            logger.error(f"Error in resolve_choice: {e}", exc_info=True)
            self.pending_choice = None
            return False

    def can_end_turn(self) -> bool:
        if not self.free_harvest_used:
            self._log("Take the FREE Harvest before ending your turn.", "warning")
            return False
        if not self.paid_action_used:
            self._log("You still have one paid action this turn.", "warning")
            return False
        return True

    def end_turn(self) -> bool:
        """Advance the turn if both action flags were used."""
        try:
            if not self.can_end_turn():
                return False

            logger.info(f"Ending turn {self.turn}")
            
            self.apply_income()
            self.resolve_random_event()
            self.apply_drift()

            self.turn += 1
            self.free_harvest_used = False
            self.paid_action_used = False
            
            # Initialize turn summary at start of new turn
            self._start_turn_summary()
            
            # Clear current turn actions for the new turn
            self.current_turn_actions = []
            
            logger.info(f"Turn advanced to {self.turn}")
            return True
        except Exception as e:
            logger.error(f"Error in end_turn: {e}", exc_info=True)
            # Try to recover by at least resetting the flags
            self.free_harvest_used = False
            self.paid_action_used = False
            return False

    # ------------------------
    # Helpers for templates
    # ------------------------
    def to_dict(self) -> Dict:
        """Convert game state to dictionary for templates"""
        try:
            return {
                "turn": self.turn,
                "max_turns": self.max_turns,
                "difficulty": self.difficulty,
                "grain": self.grain,
                "bronze": self.bronze,
                "timber": self.timber,
                "prestige": self.prestige,
                "stability": self.stability,
                "knowledge": self.knowledge,
                "elasticity": self.elasticity,
                "military": self.military,
                "collapse": self.collapse,
                "withdrawals_used": self.withdrawals_used,
                "max_withdrawals": self.max_withdrawals,
                "free_harvest_used": self.free_harvest_used,
                "paid_action_used": self.paid_action_used,
                "tech": {
                    "imperial_bureaucracy": self.tech_imperial_bureaucracy,
                    "bronze_mines": self.tech_bronze_mines,
                    "granary_network": self.tech_granary_network,
                    "alphabetic_script": self.tech_alphabetic_script,
                    "ironworking": self.tech_ironworking,
                    "diplomatic_protocols": self.tech_diplomatic_protocols,
                    "tin_trade_routes": self.tech_tin_trade_routes,
                    "phalanx_formation": self.tech_phalanx_formation,
                    "diplomatic_marriage": self.tech_diplomatic_marriage,
                },
                "builds": {
                    "granary": self.has_granary,
                    "library": self.has_library,
                    "walls": self.has_walls,
                    "bronze_mine": self.has_bronze_mine,
                    "barracks": self.has_barracks,
                    "palace": self.has_palace,
                    "lighthouse": self.has_lighthouse,
                    "watchtower": self.has_watchtower,
                },
                "message_log": self.message_log[-8:],  # show latest few
                "current_turn_actions": self.current_turn_actions,
                "previous_turn_summary": (self.previous_turn_summary.__dict__
                                          if self.previous_turn_summary else None),
                "pending_choice": (self.pending_choice.__dict__
                                  if self.pending_choice else None),
            }
        except Exception as e:
            logger.error(f"Error in to_dict: {e}", exc_info=True)
            # Return minimal valid state
            return {
                "turn": getattr(self, 'turn', 1),
                "max_turns": getattr(self, 'max_turns', 20),
                "difficulty": getattr(self, 'difficulty', 'normal'),
                "grain": getattr(self, 'grain', 50),
                "bronze": getattr(self, 'bronze', 30),
                "timber": getattr(self, 'timber', 20),
                "prestige": getattr(self, 'prestige', 10),
                "stability": getattr(self, 'stability', 65),
                "knowledge": getattr(self, 'knowledge', 40),
                "elasticity": getattr(self, 'elasticity', 50),
                "military": getattr(self, 'military', 30),
                "collapse": getattr(self, 'collapse', 45),
                "withdrawals_used": 0,
                "max_withdrawals": 3,
                "free_harvest_used": False,
                "paid_action_used": False,
                "tech": {},
                "builds": {},
                "message_log": [],
                "current_turn_actions": [],
                "previous_turn_summary": None,
                "pending_choice": None,
            }
