#!/usr/bin/env python
"""
Test script for Solution Phase
Tests the complete flow: Analysis -> Solution
"""

import sys
from my_project.crew import MyProject

def test_solution_phase():
    print("=" * 70)
    print("TESTING SOLUTION PHASE - END TO END")
    print("=" * 70)

    # Initialize BA crew with new session
    print("\nInitializing BA crew with new session...")
    ba_crew = MyProject()
    ba_crew.__post_init__(new_session=True)
    print("[OK] BA crew initialized")

    # Simulate analysis phase with pre-populated requirements
    print("\n" + "=" * 70)
    print("PHASE 1: ANALYSIS - Simulating requirement gathering")
    print("=" * 70)

    # Add requirements directly to state
    print("\nAdding requirements to state...")
    ba_crew.state_manager.add_requirement("problem_goals", "Build a task management system to organize and track team work")
    ba_crew.state_manager.add_requirement("problem_goals", "Improve visibility and coordination across development teams")

    ba_crew.state_manager.add_requirement("users_stakeholders", "20 developers who need to track their tasks")
    ba_crew.state_manager.add_requirement("users_stakeholders", "5 project managers who need to oversee team workload")

    ba_crew.state_manager.add_requirement("features_scope", "Create tasks with title and description")
    ba_crew.state_manager.add_requirement("features_scope", "Assign tasks to team members")
    ba_crew.state_manager.add_requirement("features_scope", "Set deadlines for tasks")
    ba_crew.state_manager.add_requirement("features_scope", "Track task progress and status")
    ba_crew.state_manager.add_requirement("features_scope", "View team workload and reports")

    print("[OK] Requirements added")

    # Show requirements summary
    print("\n" + "-" * 70)
    print("REQUIREMENTS SUMMARY:")
    print("-" * 70)
    print(ba_crew.state_manager.get_all_requirements_text())

    # Check if analysis is complete
    is_complete, reason = ba_crew.state_manager.is_analysis_complete()
    print("\n" + "-" * 70)
    print(f"Analysis Complete: {is_complete}")
    print(f"Reason: {reason}")
    print("-" * 70)

    if not is_complete:
        print("\n[ERROR] Analysis phase not complete. Cannot proceed to solution phase.")
        return False

    # Run solution phase
    print("\n" + "=" * 70)
    print("PHASE 2: SOLUTION - Running solution design")
    print("=" * 70)

    try:
        print("\n[INFO] Solution Designer is working...")
        print("[INFO] This may take a few moments...")
        print("-" * 70)

        design_summary, validation_report, phase_eval, should_transition = ba_crew.run_solution_phase()

        # Display results
        print("\n" + "=" * 70)
        print("SOLUTION PHASE COMPLETED")
        print("=" * 70)

        print("\n" + "-" * 70)
        print("1. DESIGN SUMMARY:")
        print("-" * 70)
        print(design_summary)

        print("\n" + "-" * 70)
        print("2. VALIDATION REPORT:")
        print("-" * 70)
        print(validation_report)

        print("\n" + "-" * 70)
        print("3. PHASE EVALUATION:")
        print("-" * 70)
        print(phase_eval)

        print("\n" + "-" * 70)
        print("4. COMPLETE SOLUTION:")
        print("-" * 70)
        print(ba_crew.state_manager.get_solution_text())

        # Check solution completeness
        is_solution_complete, solution_reason = ba_crew.state_manager.is_solution_complete()
        print("\n" + "-" * 70)
        print(f"Solution Complete: {is_solution_complete}")
        print(f"Reason: {solution_reason}")
        print(f"Ready for Documentation: {should_transition}")
        print("-" * 70)

        # Show final state summary
        print("\n" + "=" * 70)
        print("FINAL STATE SUMMARY")
        print("=" * 70)
        print(ba_crew.state_manager.get_conversation_summary())
        print("\n" + ba_crew.state_manager.get_solution_summary())

        print("\n" + "=" * 70)
        print("[SUCCESS] Solution phase test completed!")
        print("State saved to: conversation_state.json")
        print("=" * 70)

        return True

    except Exception as e:
        print(f"\n[ERROR] Solution phase failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_solution_phase()
    sys.exit(0 if success else 1)
