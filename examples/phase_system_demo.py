"""
Example demonstrating the Game Loop & Phase System.

This example shows how the PhaseManager orchestrates a complete game loop
with proper phase transitions and constraint enforcement.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from core import PhaseManager, PhaseType, ControlPointConstraintError, InvalidPhaseTransitionError


def main():
    """Demonstrate the phase system with a simulated game loop."""
    print("=" * 60)
    print("PathWars - Game Loop & Phase System Demo")
    print("=" * 60)
    
    # Initialize phase manager for a 3-round match
    phase_manager = PhaseManager(max_rounds=3)
    
    print(f"\n🎮 Starting new match with {phase_manager.max_rounds} rounds")
    print(f"Current Phase: {phase_manager.current_phase.phase_type.name}")
    print(f"Round: {phase_manager.current_round}")
    
    # === ROUND 1: PREPARATION PHASE ===
    print("\n" + "=" * 60)
    print("ROUND 1: PREPARATION PHASE")
    print("=" * 60)
    
    # Place initial 2 points on borders
    print("\n📍 Placing initial control points...")
    
    # Validate and place start point (left border, x=0)
    try:
        phase_manager.validate_initial_point_placement(
            x=0, y=10, grid_width=20, grid_height=20, is_start_point=True
        )
        phase_manager.register_point_added(0)
        print(f"  ✓ Start point placed at (0, 10)")
        print(f"    Points placed: {phase_manager.initial_points_placed}/2")
    except ControlPointConstraintError as e:
        print(f"  ✗ Error: {e}")
    
    # Validate and place end point (right border, x=19)
    try:
        phase_manager.validate_initial_point_placement(
            x=19, y=10, grid_width=20, grid_height=20, is_start_point=False
        )
        phase_manager.register_point_added(1)
        print(f"  ✓ End point placed at (19, 10)")
        print(f"    Points placed: {phase_manager.initial_points_placed}/2")
    except ControlPointConstraintError as e:
        print(f"  ✗ Error: {e}")
    
    # Try to place a third point (should fail)
    print("\n❌ Attempting to place a third point (should fail)...")
    try:
        phase_manager.register_point_added(2)
        print("  ✗ Unexpected: Third point was allowed!")
    except ControlPointConstraintError as e:
        print(f"  ✓ Correctly rejected: {e}")
    
    # Transition to building phase
    print("\n🔄 Transitioning to BUILDING phase...")
    phase_manager.transition_to(PhaseType.BUILDING)
    print(f"  ✓ Current phase: {phase_manager.current_phase.phase_type.name}")
    print(f"    Can place towers: {phase_manager.current_phase.can_place_tower()}")
    print(f"    Can modify path: {phase_manager.current_phase.can_modify_path()}")
    
    # Build some towers
    print("\n🗼 Placing towers...")
    print("  ✓ Tower placed at (5, 8)")
    print("  ✓ Tower placed at (10, 12)")
    
    # Transition to combat
    print("\n🔄 Transitioning to COMBAT phase...")
    phase_manager.transition_to(PhaseType.COMBAT)
    print(f"  ✓ Current phase: {phase_manager.current_phase.phase_type.name}")
    print(f"    Can place towers: {phase_manager.current_phase.can_place_tower()}")
    
    # Simulate combat
    print("\n⚔️  Combat in progress...")
    print("  → Wave spawning...")
    print("  → Towers attacking...")
    print("  → Wave cleared!")
    
    # Transition to round end
    print("\n🔄 Transitioning to ROUND_END phase...")
    phase_manager.transition_to(PhaseType.ROUND_END)
    print(f"  ✓ Current phase: {phase_manager.current_phase.phase_type.name}")
    print(f"  ✓ Round {phase_manager.current_round} complete!")
    
    # === ROUND 2: PATH MODIFICATION PHASE ===
    print("\n" + "=" * 60)
    print("ROUND 2: PATH MODIFICATION PHASE")
    print("=" * 60)
    
    phase_manager.transition_to(PhaseType.PATH_MODIFICATION)
    print(f"\nCurrent Phase: {phase_manager.current_phase.phase_type.name}")
    print(f"Round: {phase_manager.current_round}")
    print(f"Points modified this round: {phase_manager.points_modified_this_round}")
    
    # Try to modify a point from round 1 (should fail - points are locked)
    print("\n❌ Attempting to move point from Round 1 (should fail)...")
    can_move = phase_manager.can_move_control_point(0)
    print(f"  Can move point 0 (from Round 1): {can_move}")
    
    # Add a new control point (allowed, max 1 per round)
    print("\n📍 Adding new control point in Round 2...")
    try:
        phase_manager.register_point_added(2)
        print(f"  ✓ Point 2 added")
        print(f"    Points modified: {phase_manager.points_modified_this_round}/1")
    except ControlPointConstraintError as e:
        print(f"  ✗ Error: {e}")
    
    # Try to add another point (should fail - already modified 1)
    print("\n❌ Attempting to add another point (should fail - limit reached)...")
    try:
        phase_manager.register_point_added(3)
        print("  ✗ Unexpected: Second modification was allowed!")
    except ControlPointConstraintError as e:
        print(f"  ✓ Correctly rejected: {e}")
    
    # Can send mercenaries in this phase
    print("\n💰 Sending mercenaries to opponent...")
    if phase_manager.current_phase.can_send_mercenaries():
        print("  ✓ Mercenary 'SpeedyVariableX' queued")
    
    # Can research in this phase
    print("\n🔬 Conducting research...")
    if phase_manager.current_phase.can_research():
        print("  ✓ Research 'LAGRANGE_INTERPOLATION' unlocked")
    
    # Complete Round 2
    print("\n🔄 Completing Round 2...")
    phase_manager.transition_to(PhaseType.BUILDING)
    phase_manager.transition_to(PhaseType.COMBAT)
    print("  ⚔️  Combat...")
    phase_manager.transition_to(PhaseType.ROUND_END)
    print(f"  ✓ Round {phase_manager.current_round} complete!")
    
    # === ROUND 3: FINAL ROUND ===
    print("\n" + "=" * 60)
    print("ROUND 3: FINAL ROUND")
    print("=" * 60)
    
    phase_manager.transition_to(PhaseType.PATH_MODIFICATION)
    print(f"\nRound: {phase_manager.current_round}")
    print(f"Modifications reset: {phase_manager.points_modified_this_round}/1 available")
    
    # Complete the match
    phase_manager.transition_to(PhaseType.BUILDING)
    phase_manager.transition_to(PhaseType.COMBAT)
    phase_manager.transition_to(PhaseType.ROUND_END)
    
    print(f"\n🏁 Round {phase_manager.current_round} complete!")
    
    # Try to continue (should indicate match is complete)
    phase_manager.transition_to(PhaseType.PATH_MODIFICATION)
    print(f"\nMatch Status:")
    print(f"  Current Round: {phase_manager.current_round}")
    print(f"  Max Rounds: {phase_manager.max_rounds}")
    print(f"  Match Complete: {phase_manager.is_match_complete()}")
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ Phase System Demo Complete!")
    print("=" * 60)
    print("\nKey Features Demonstrated:")
    print("  ✓ State Pattern for phase management")
    print("  ✓ Preparation phase with 2 initial points")
    print("  ✓ Border validation for initial points")
    print("  ✓ Max 1 point modification per round (rounds 2+)")
    print("  ✓ Point locking from previous rounds")
    print("  ✓ Round tracking and match completion")
    print("  ✓ Phase-specific action permissions")
    print("  ✓ Transition validation")
    

if __name__ == "__main__":
    main()
