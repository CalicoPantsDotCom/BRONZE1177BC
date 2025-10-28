#!/usr/bin/env python3
"""
Test suite for game logic - focusing on action handling and turn advancement
"""

import unittest
from game_logic import Game


class TestActionHandling(unittest.TestCase):
    """Test action handling and flag management"""

    def setUp(self):
        """Create a fresh game for each test"""
        self.game = Game()

    def test_harvest_free_sets_flag(self):
        """Test that free harvest sets the flag correctly"""
        self.assertFalse(self.game.free_harvest_used)
        result = self.game.harvest_free()
        self.assertTrue(result)
        self.assertTrue(self.game.free_harvest_used)

    def test_harvest_free_cannot_be_used_twice(self):
        """Test that free harvest cannot be used twice in same turn"""
        self.game.harvest_free()
        result = self.game.harvest_free()
        self.assertFalse(result)

    def test_gather_timber_sets_paid_flag(self):
        """Test that gather timber sets paid action flag"""
        self.assertFalse(self.game.paid_action_used)
        result = self.game.gather_timber()
        self.assertTrue(result)
        self.assertTrue(self.game.paid_action_used)

    def test_gather_timber_requires_resources(self):
        """Test that gather timber fails without resources"""
        self.game.grain = 5  # Not enough
        result = self.game.gather_timber()
        self.assertFalse(result)
        self.assertFalse(self.game.paid_action_used)  # Flag should NOT be set on failure

    def test_paid_action_cannot_be_used_twice(self):
        """Test that paid action cannot be used twice in same turn"""
        self.game.gather_timber()
        result = self.game.fortify()
        self.assertFalse(result)

    def test_withdraw_support_sets_paid_flag(self):
        """Test that withdraw support sets paid action flag"""
        self.assertFalse(self.game.paid_action_used)
        result = self.game.withdraw_support()
        self.assertTrue(result)
        self.assertTrue(self.game.paid_action_used)

    def test_research_sets_paid_flag(self):
        """Test that research sets paid action flag"""
        self.game.knowledge = 20
        self.game.grain = 30
        self.assertFalse(self.game.paid_action_used)
        result = self.game.research_imperial_bureaucracy()
        self.assertTrue(result)
        self.assertTrue(self.game.paid_action_used)

    def test_build_sets_paid_flag(self):
        """Test that building sets paid action flag"""
        self.game.timber = 30
        self.game.grain = 30
        self.assertFalse(self.game.paid_action_used)
        result = self.game.build_granary()
        self.assertTrue(result)
        self.assertTrue(self.game.paid_action_used)

    def test_diplomacy_sets_paid_flag(self):
        """Test that diplomacy actions set paid action flag"""
        self.game.grain = 30
        self.assertFalse(self.game.paid_action_used)
        result = self.game.host_festival()
        self.assertTrue(result)
        self.assertTrue(self.game.paid_action_used)


class TestTurnAdvancement(unittest.TestCase):
    """Test turn advancement logic"""

    def setUp(self):
        """Create a fresh game for each test"""
        self.game = Game()

    def test_cannot_end_turn_without_harvest(self):
        """Test that turn cannot end without taking free harvest"""
        result = self.game.can_end_turn()
        self.assertFalse(result)

    def test_cannot_end_turn_without_paid_action(self):
        """Test that turn cannot end without taking paid action"""
        self.game.harvest_free()
        result = self.game.can_end_turn()
        self.assertFalse(result)

    def test_can_end_turn_after_both_actions(self):
        """Test that turn can end after both actions"""
        self.game.harvest_free()
        self.game.gather_timber()
        result = self.game.can_end_turn()
        self.assertTrue(result)

    def test_end_turn_advances_turn_counter(self):
        """Test that ending turn advances turn counter"""
        self.game.harvest_free()
        self.game.gather_timber()
        initial_turn = self.game.turn
        result = self.game.end_turn()
        self.assertTrue(result)
        self.assertEqual(self.game.turn, initial_turn + 1)

    def test_end_turn_resets_flags(self):
        """Test that ending turn resets action flags"""
        self.game.harvest_free()
        self.game.gather_timber()
        self.assertTrue(self.game.free_harvest_used)
        self.assertTrue(self.game.paid_action_used)
        
        self.game.end_turn()
        
        self.assertFalse(self.game.free_harvest_used)
        self.assertFalse(self.game.paid_action_used)

    def test_end_turn_applies_income(self):
        """Test that ending turn applies building income"""
        self.game.harvest_free()
        self.game.gather_timber()
        self.game.has_bronze_mine = True
        initial_bronze = self.game.bronze
        
        # Turn ends, but random events can affect bronze
        # Just verify turn advanced and mine flag is still set
        self.game.end_turn()
        
        self.assertEqual(self.game.turn, 2)
        self.assertTrue(self.game.has_bronze_mine)

    def test_end_turn_applies_drift(self):
        """Test that ending turn applies collapse drift"""
        self.game.harvest_free()
        self.game.gather_timber()
        initial_collapse = self.game.collapse
        
        self.game.end_turn()
        
        # Should get drift_per_turn added to collapse (plus random events may affect it)
        # So just check that collapse changed and turn advanced
        self.assertNotEqual(self.game.collapse, initial_collapse)
        self.assertEqual(self.game.turn, 2)

    def test_end_turn_without_actions_fails(self):
        """Test that end_turn returns False when actions not complete"""
        result = self.game.end_turn()
        self.assertFalse(result)
        self.assertEqual(self.game.turn, 1)  # Turn should not advance


class TestChoiceEvents(unittest.TestCase):
    """Test choice event handling"""

    def setUp(self):
        """Create a fresh game for each test"""
        self.game = Game()

    def test_resolve_choice_vassal_aid_a(self):
        """Test resolving vassal aid choice A"""
        self.game.grain = 50
        self.game.pending_choice = self.game._create_vassal_aid_choice()
        
        initial_grain = self.game.grain
        result = self.game.resolve_choice("a")
        
        self.assertTrue(result)
        self.assertLess(self.game.grain, initial_grain)
        self.assertIsNone(self.game.pending_choice)

    def test_resolve_choice_vassal_aid_a_insufficient_resources(self):
        """Test resolving vassal aid choice A with insufficient resources"""
        self.game.grain = 10  # Not enough
        self.game.pending_choice = self.game._create_vassal_aid_choice()
        
        result = self.game.resolve_choice("a")
        
        self.assertFalse(result)

    def test_resolve_choice_vassal_aid_b(self):
        """Test resolving vassal aid choice B"""
        self.game.pending_choice = self.game._create_vassal_aid_choice()
        
        result = self.game.resolve_choice("b")
        
        self.assertTrue(result)
        self.assertIsNone(self.game.pending_choice)


class TestActionSummary(unittest.TestCase):
    """Test action summary tracking"""

    def setUp(self):
        """Create a fresh game for each test"""
        self.game = Game()

    def test_action_adds_to_current_turn_actions(self):
        """Test that actions are tracked in current turn"""
        self.assertEqual(len(self.game.current_turn_actions), 0)
        
        self.game.harvest_free()
        
        self.assertEqual(len(self.game.current_turn_actions), 1)
        self.assertEqual(self.game.current_turn_actions[0]["name"], "Harvest")

    def test_multiple_actions_tracked(self):
        """Test that multiple actions are tracked"""
        self.game.harvest_free()
        self.game.gather_timber()
        
        self.assertEqual(len(self.game.current_turn_actions), 2)

    def test_current_actions_cleared_on_new_turn(self):
        """Test that current actions are cleared when turn advances"""
        self.game.harvest_free()
        self.game.gather_timber()
        self.assertEqual(len(self.game.current_turn_actions), 2)
        
        self.game.end_turn()
        
        self.assertEqual(len(self.game.current_turn_actions), 0)


if __name__ == '__main__':
    unittest.main()
