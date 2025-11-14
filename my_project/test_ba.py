#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple test script for BA system - simulates a conversation
"""
import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')

sys.path.insert(0, 'src')

from my_project.crew import MyProject

def test_ba_conversation():
    """Test the BA system with simulated user inputs"""

    print("=" * 70)
    print("TESTING BUSINESS ANALYST SYSTEM - ANALYSIS PHASE")
    print("=" * 70)
    print()

    # Initialize BA crew
    print("Initializing BA crew...")
    ba_crew = MyProject()
    ba_crew.__post_init__()
    print("[OK] BA crew initialized successfully")
    print()

    # Simulated conversation
    test_messages = [
        "I want to build a task management app for my team",
        "We have about 20 developers and 5 project managers who need to track their work",
        "We need features like creating tasks, assigning them to team members, setting deadlines, and tracking progress"
    ]

    for i, user_message in enumerate(test_messages, 1):
        print("=" * 70)
        print(f"TURN {i}")
        print("=" * 70)
        print(f"\n[USER] {user_message}")
        print("\n[BA AGENT] Processing...")
        print("-" * 70)

        try:
            ba_response, should_transition, phase_eval = ba_crew.run_analysis_conversation(user_message)

            print(f"\n[BA RESPONSE]")
            print(ba_response)
            print()

            if should_transition:
                print("\n" + "=" * 70)
                print("[SUCCESS] ANALYSIS PHASE COMPLETE!")
                print("=" * 70)
                print("\n[PHASE EVALUATION]")
                print(phase_eval)
                break

        except Exception as e:
            print(f"\n[ERROR] {e}")
            import traceback
            traceback.print_exc()
            break

    # Show final summary
    print("\n" + "=" * 70)
    print("[FINAL REQUIREMENTS SUMMARY]")
    print("=" * 70)
    print(ba_crew.state_manager.get_all_requirements_text())
    print()
    print("[CONVERSATION SUMMARY]")
    print(ba_crew.state_manager.get_conversation_summary())
    print()
    print("=" * 70)
    print("Test completed! Check conversation_state.json for saved state.")
    print("=" * 70)

if __name__ == "__main__":
    test_ba_conversation()
