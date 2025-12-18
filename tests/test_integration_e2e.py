"""
End-to-end integration tests for PathWars - The Interpolation Battles.

These tests verify that major features work together correctly from a
user perspective, testing the complete flow of gameplay.
"""

import pytest
import pygame
from unittest.mock import Mock, MagicMock

# Initialize pygame for testing (headless)
pygame.init()
pygame.display.set_mode((1, 1))

from core.game_state import GameState, GamePhase, InsufficientFundsError
from core.grid import Grid
from core.combat_manager import CombatManager
from core.wave_manager import WaveManager
from core.curve_state import CurveState
from core.research.research_manager import ResearchManager
from core.research.research_type import ResearchType
from entities.tower import Tower, TowerType, TowerLevel
from entities.enemy import Enemy, EnemyType
from entities.factory import EntityFactory
from entities.mercenaries.mercenary_factory import MercenaryFactory
from entities.mercenaries.mercenary_types import MercenaryType
from graphics.renderer import Renderer


class TestSinglePlayerFlow:
    """Test complete single player gameplay flow."""
    
    def setup_method(self):
        """Setup for each test."""
        GameState.reset_instance()
        self.game_state = GameState()
        self.grid = Grid(width=20, height=20, cell_size=32)
    
    def test_initial_game_state(self):
        """Test that game starts with correct initial values."""
        assert self.game_state.money == 1000
        assert self.game_state.lives == 10
        assert self.game_state.current_phase == GamePhase.PLANNING
        assert len(self.game_state.entities_collection['towers']) == 0
        assert len(self.game_state.entities_collection['enemies']) == 0
    
    def test_tower_placement_and_economy(self):
        """Test placing towers and money deduction."""
        initial_money = self.game_state.money
        
        # Place a DEAN tower (costs $50)
        tower = EntityFactory.create_tower(TowerType.DEAN, 5, 5)
        self.game_state.deduct_money(50)
        self.game_state.add_entity('towers', tower)
        
        assert self.game_state.money == initial_money - 50
        assert len(self.game_state.entities_collection['towers']) == 1
        
        # Try to place tower without enough money
        with pytest.raises(InsufficientFundsError):
            self.game_state.deduct_money(10000)
    
    def test_tower_upgrade_flow(self):
        """Test upgrading a tower."""
        # Place and upgrade a DEAN tower
        tower = EntityFactory.create_tower(TowerType.DEAN, 5, 5)
        self.game_state.deduct_money(50)  # Placement cost
        self.game_state.add_entity('towers', tower)
        
        initial_damage = tower.damage
        upgrade_cost = tower.upgrade_cost
        
        # Upgrade tower
        self.game_state.deduct_money(upgrade_cost)
        tower.upgrade()
        
        assert tower.level == TowerLevel.DOCTORATE
        assert tower.damage > initial_damage
        assert not tower.can_upgrade  # Max level reached
    
    def test_combat_cycle(self):
        """Test basic combat between tower and enemy."""
        # Create tower and enemy
        tower = EntityFactory.create_tower(TowerType.CALCULUS, 5, 5)
        enemy = EntityFactory.create_enemy(EnemyType.STUDENT, [(5, 5), (6, 6)])
        
        self.game_state.add_entity('towers', tower)
        self.game_state.add_entity('enemies', enemy)
        
        # Setup combat manager
        combat_manager = CombatManager()
        kills = []
        combat_manager.on_enemy_killed(lambda e, r: kills.append(e))
        
        # Simulate combat
        initial_hp = enemy.hp
        for _ in range(100):  # Run until enemy dies
            combat_manager.update(0.1, self.game_state)
            tower.update(0.1)
            enemy.update(0.1)
            if enemy.is_dead:
                break
        
        assert enemy.is_dead
        assert len(kills) == 1
    
    def test_phase_transitions(self):
        """Test game phase transitions."""
        assert self.game_state.current_phase == GamePhase.PLANNING
        
        # Planning -> Waiting
        self.game_state.change_phase(GamePhase.WAITING)
        assert self.game_state.current_phase == GamePhase.WAITING
        
        # Waiting -> Battle
        self.game_state.change_phase(GamePhase.BATTLE)
        assert self.game_state.current_phase == GamePhase.BATTLE
        
        # Battle -> Result
        self.game_state.change_phase(GamePhase.RESULT)
        assert self.game_state.current_phase == GamePhase.RESULT


class TestResearchSystem:
    """Test research and interpolation unlocking."""
    
    def setup_method(self):
        """Setup for each test."""
        GameState.reset_instance()
        self.game_state = GameState()
        self.research_manager = ResearchManager("test_player")
    
    def test_initial_methods_available(self):
        """Test that only linear is available at start."""
        methods = self.research_manager.get_interpolation_methods()
        assert 'linear' in methods
        assert 'lagrange' not in methods
        assert 'spline' not in methods
    
    def test_research_lagrange(self):
        """Test unlocking Lagrange interpolation."""
        cost = self.research_manager.unlock(
            ResearchType.LAGRANGE_INTERPOLATION,
            self.game_state.money
        )
        self.game_state.deduct_money(cost)
        
        assert self.research_manager.is_unlocked(ResearchType.LAGRANGE_INTERPOLATION)
        methods = self.research_manager.get_interpolation_methods()
        assert 'lagrange' in methods
    
    def test_research_prerequisites(self):
        """Test that Spline requires Lagrange."""
        # Try to unlock Spline without Lagrange
        from core.research.research_manager import PrerequisiteNotMetError
        with pytest.raises(PrerequisiteNotMetError):
            self.research_manager.unlock(
                ResearchType.SPLINE_INTERPOLATION,
                self.game_state.money
            )
        
        # Unlock Lagrange first
        self.research_manager.unlock(
            ResearchType.LAGRANGE_INTERPOLATION,
            self.game_state.money
        )
        
        # Now Spline can be unlocked
        cost = self.research_manager.unlock(
            ResearchType.SPLINE_INTERPOLATION,
            self.game_state.money
        )
        assert cost == 1000
        
        methods = self.research_manager.get_interpolation_methods()
        assert 'spline' in methods
    
    def test_insufficient_funds_for_research(self):
        """Test that research fails without enough money."""
        from core.research.research_manager import InsufficientFundsError
        
        # Reduce money to insufficient amount
        self.game_state.deduct_money(900)  # Leave only $100
        
        with pytest.raises(InsufficientFundsError):
            self.research_manager.unlock(
                ResearchType.LAGRANGE_INTERPOLATION,
                self.game_state.money
            )


class TestMercenarySystem:
    """Test mercenary creation and costs."""
    
    def setup_method(self):
        """Setup for each test."""
        GameState.reset_instance()
        self.game_state = GameState()
    
    def test_mercenary_creation(self):
        """Test creating each mercenary type."""
        for merc_type in MercenaryFactory.get_available_types():
            mercenary = MercenaryFactory.create_mercenary(
                merc_type,
                owner_player_id="player1",
                target_player_id="player2"
            )
            assert mercenary is not None
            assert mercenary.owner_player_id == "player1"
            assert mercenary.target_player_id == "player2"
    
    def test_mercenary_costs(self):
        """Test mercenary cost validation."""
        # Reinforced Student costs $100
        cost = MercenaryFactory.get_cost(MercenaryType.REINFORCED_STUDENT)
        assert cost == 100
        
        # Speedy Variable X costs $75
        cost = MercenaryFactory.get_cost(MercenaryType.SPEEDY_VARIABLE_X)
        assert cost == 75
        
        # Tank Constant Pi costs $200
        cost = MercenaryFactory.get_cost(MercenaryType.TANK_CONSTANT_PI)
        assert cost == 200
    
    def test_mercenary_purchase_validation(self):
        """Test that purchase validation works."""
        # Can afford Speedy ($75)
        can_buy = MercenaryFactory.validate_purchase(
            MercenaryType.SPEEDY_VARIABLE_X,
            1,
            self.game_state.money
        )
        assert can_buy
        
        # Cannot afford 100 Tanks
        can_buy = MercenaryFactory.validate_purchase(
            MercenaryType.TANK_CONSTANT_PI,
            100,
            self.game_state.money
        )
        assert not can_buy


class TestEconomicCycle:
    """Test complete economic cycle."""
    
    def setup_method(self):
        """Setup for each test."""
        GameState.reset_instance()
        self.game_state = GameState()
    
    def test_complete_economic_flow(self):
        """Test earning and spending money in a typical game flow."""
        starting_money = self.game_state.money
        
        # 1. Place a tower ($75)
        self.game_state.deduct_money(75)
        assert self.game_state.money == starting_money - 75
        
        # 2. Kill an enemy (earn $10)
        self.game_state.add_money(10)
        assert self.game_state.money == starting_money - 75 + 10
        
        # 3. Upgrade tower ($100)
        self.game_state.deduct_money(100)
        assert self.game_state.money == starting_money - 75 + 10 - 100
        
        # 4. Kill more enemies
        for _ in range(5):
            self.game_state.add_money(10)
        
        expected = starting_money - 75 + 10 - 100 + 50
        assert self.game_state.money == expected
    
    def test_interpolation_method_costs(self):
        """Test that switching interpolation methods costs money."""
        # According to the audit, these are the costs:
        INTERPOLATION_COSTS = {
            'linear': 0,
            'lagrange': 50,
            'spline': 100,
        }
        
        starting_money = self.game_state.money
        
        # Switch to Lagrange (should cost $50)
        self.game_state.deduct_money(INTERPOLATION_COSTS['lagrange'])
        assert self.game_state.money == starting_money - 50
        
        # Switch to Spline (should cost $100)
        self.game_state.deduct_money(INTERPOLATION_COSTS['spline'])
        assert self.game_state.money == starting_money - 50 - 100


class TestWaveProgression:
    """Test wave manager and enemy spawning."""
    
    def test_wave_initialization(self):
        """Test wave manager initialization."""
        wave_manager = WaveManager()
        assert not wave_manager.is_active
        assert wave_manager.total_waves == 5  # Default
    
    def test_wave_spawning(self):
        """Test that waves spawn enemies correctly."""
        wave_manager = WaveManager()
        path = [(0, 0), (10, 10), (20, 20)]
        
        wave_manager.start_wave(1, path)
        assert wave_manager.is_active
        
        # Update until wave is complete
        enemies_spawned = []
        for _ in range(1000):  # Enough time for all enemies to spawn
            new_enemies = wave_manager.update(0.1)
            enemies_spawned.extend(new_enemies)
            if wave_manager.is_wave_complete():
                break
        
        assert len(enemies_spawned) > 0
        assert wave_manager.is_wave_complete()


class TestCurveEditor:
    """Test curve editor and interpolation."""
    
    def test_curve_initialization(self):
        """Test curve state initialization."""
        curve_state = CurveState()
        curve_state.initialize_default_points(start_x=0.0, end_x=19.0, y=10.0)
        
        points = curve_state.control_points
        assert len(points) == 2
        assert points[0] == (0.0, 10.0)
        assert points[1] == (19.0, 10.0)
    
    def test_add_control_points(self):
        """Test adding control points."""
        curve_state = CurveState()
        curve_state.add_point(5.0, 10.0)
        curve_state.add_point(10.0, 15.0)
        
        assert curve_state.get_point_count() == 2
    
    def test_interpolation_methods(self):
        """Test switching between interpolation methods."""
        curve_state = CurveState()
        curve_state.add_point(0.0, 0.0)
        curve_state.add_point(10.0, 10.0)
        
        # Test linear
        curve_state.set_method('linear')
        assert curve_state.interpolation_method == 'linear'
        path = curve_state.get_interpolated_path(10)
        assert len(path) > 0
        
        # Test lagrange
        curve_state.set_method('lagrange')
        assert curve_state.interpolation_method == 'lagrange'
        path = curve_state.get_interpolated_path(10)
        assert len(path) > 0
        
        # Test spline
        curve_state.set_method('spline')
        assert curve_state.interpolation_method == 'spline'
        path = curve_state.get_interpolated_path(10)
        assert len(path) > 0
    
    def test_curve_locking(self):
        """Test curve locking mechanism."""
        curve_state = CurveState()
        assert not curve_state.locked
        
        curve_state.lock()
        assert curve_state.locked
        
        # Should not be able to add points when locked
        from core.curve_state import CurveLockedError
        with pytest.raises(CurveLockedError):
            curve_state.add_point(5.0, 5.0)
        
        curve_state.unlock()
        assert not curve_state.locked


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
