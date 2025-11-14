#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from my_project.crew import MyProject

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the Business Analyst interactive conversation for Analysis phase.
    """
    print("=" * 70, flush=True)
    print("BUSINESS ANALYST - Requirements Gathering System", flush=True)
    print("=" * 70, flush=True)
    print("\nWelcome! I'm your Business Analyst assistant.", flush=True)
    print("I'll help you gather requirements for your software project.", flush=True)
    print("\nPhase: ANALYSIS", flush=True)
    print("Focus: Understanding your problem, users, and desired features", flush=True)
    print("\nType 'quit' or 'exit' to end the session.", flush=True)
    print("Type 'status' to see collected requirements.", flush=True)
    print("=" * 70, flush=True)
    print(flush=True)

    try:
        # Check if user wants to start new session or continue existing
        import os
        has_existing = os.path.exists("conversation_state.json")
        new_session = True  # Default: always start fresh

        if has_existing:
            choice = input("Found existing session. Continue? (y/n, default=n): ").strip().lower()
            new_session = choice != 'y'

        print("Initializing BA system (this may take a moment)...", flush=True)
        ba_crew = MyProject.create(new_session=new_session)
        print("BA system ready!", flush=True)

        # Start conversation loop
        turn_count = 0

        while True:
            # Get user input
            print("\n" + "-" * 70)
            user_input = input("\nYou: ").strip()

            if not user_input:
                continue

            # Check for exit commands
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\n" + "=" * 70)
                print("Session ended. Requirements saved to conversation_state.json")
                print("=" * 70)

                # Show final summary
                print("\n📋 FINAL REQUIREMENTS SUMMARY:")
                print(ba_crew.state_manager.get_all_requirements_text())
                break

            # Check for status command
            if user_input.lower() == 'status':
                print("\n" + "=" * 70)
                print("📊 CURRENT STATUS:")
                print("=" * 70)
                print(ba_crew.state_manager.get_conversation_summary())
                print("\n📋 COLLECTED REQUIREMENTS:")
                print(ba_crew.state_manager.get_all_requirements_text())
                continue

            # Process user message through BA crew
            turn_count += 1
            print(f"\n🤖 BA Agent is thinking... (Turn {turn_count})")
            print("-" * 70)

            try:
                ba_response, should_transition, phase_eval = ba_crew.run_analysis_conversation(user_input)

                # Display BA response
                print(f"\n💼 Business Analyst:\n{ba_response}")

                # Check if ready to transition
                if should_transition:
                    print("\n" + "=" * 70, flush=True)
                    print("✅ ANALYSIS PHASE COMPLETE!", flush=True)
                    print("=" * 70, flush=True)
                    print("\n📊 Phase Evaluation:", flush=True)
                    print(phase_eval, flush=True)
                    print("\n📋 COLLECTED REQUIREMENTS:", flush=True)
                    print(ba_crew.state_manager.get_all_requirements_text(), flush=True)
                    print("\n" + "=" * 70, flush=True)
                    print("🚀 Moving to SOLUTION phase...", flush=True)
                    print("=" * 70, flush=True)

                    # Run solution phase
                    try:
                        print("\n🎨 Solution Designer is working...", flush=True)
                        print("This may take a few moments...", flush=True)
                        print("-" * 70, flush=True)

                        design_summary, validation_report, solution_eval, should_transition_to_doc = ba_crew.run_solution_phase()

                        # Reload state to get updated solution components
                        ba_crew.state_manager = ba_crew.state_manager.__class__(ba_crew.state_manager.state_file, new_session=False)
                        ba_crew.state_tool.state_manager = ba_crew.state_manager
                        ba_crew.solution_tool.state_manager = ba_crew.state_manager

                        # Display solution results
                        print("\n" + "=" * 70, flush=True)
                        print("✅ SOLUTION PHASE COMPLETE!", flush=True)
                        print("=" * 70, flush=True)

                        print("\n📐 Solution Design Summary:", flush=True)
                        print(design_summary, flush=True)

                        print("\n✔️ Validation Report:", flush=True)
                        print(validation_report, flush=True)

                        print("\n📊 Phase Evaluation:", flush=True)
                        print(solution_eval, flush=True)

                        print("\n" + "=" * 70, flush=True)
                        print("📋 COMPLETE SOLUTION:", flush=True)
                        print("=" * 70, flush=True)
                        print(ba_crew.state_manager.get_solution_text(), flush=True)

                        if should_transition_to_doc:
                            print("\n" + "=" * 70, flush=True)
                            print("🚀 Moving to DOCUMENTATION phase...", flush=True)
                            print("=" * 70, flush=True)

                            # ========== PRODUCT BRIEF PHASE (with revision loop) ==========
                            brief_attempt = 0
                            max_brief_attempts = 3
                            revision_feedback = ""

                            while brief_attempt < max_brief_attempts:
                                brief_attempt += 1
                                print(f"\n📝 Creating Product Brief (Attempt {brief_attempt}/{max_brief_attempts})...", flush=True)
                                print("-" * 70, flush=True)

                                try:
                                    brief_text, needs_revision, review_report = ba_crew.run_product_brief_phase(revision_feedback)

                                    # Reload state
                                    ba_crew.state_manager = ba_crew.state_manager.__class__(ba_crew.state_manager.state_file, new_session=False)
                                    ba_crew.state_tool.state_manager = ba_crew.state_manager
                                    ba_crew.solution_tool.state_manager = ba_crew.state_manager
                                    ba_crew.documentation_tool.state_manager = ba_crew.state_manager

                                    print("\n" + "=" * 70, flush=True)
                                    print("📄 PRODUCT BRIEF", flush=True)
                                    print("=" * 70, flush=True)
                                    print(brief_text, flush=True)

                                    print("\n" + "=" * 70, flush=True)
                                    print("📊 REVIEW REPORT", flush=True)
                                    print("=" * 70, flush=True)
                                    print(review_report, flush=True)

                                    # Ask user for decision
                                    print("\n" + "=" * 70, flush=True)
                                    decision = input("Approve Product Brief? (approve/revise/cancel): ").strip().lower()

                                    if decision in ['approve', 'a']:
                                        print("\n✅ Product Brief approved!", flush=True)
                                        break
                                    elif decision in ['cancel', 'c']:
                                        print("\n❌ Documentation phase cancelled.", flush=True)
                                        break
                                    elif decision in ['revise', 'r']:
                                        if brief_attempt >= max_brief_attempts:
                                            print(f"\n⚠️ Maximum revision attempts ({max_brief_attempts}) reached.", flush=True)
                                            break
                                        revision_feedback = input("\nWhat needs to be revised? (be specific): ").strip()
                                        if not revision_feedback:
                                            print("\n⚠️ No feedback provided. Using previous version.", flush=True)
                                            break
                                        print(f"\n🔄 Revising Product Brief based on feedback...", flush=True)
                                    else:
                                        print("\n⚠️ Invalid input. Treating as 'approve'.", flush=True)
                                        break

                                except Exception as e:
                                    print(f"\n❌ Error during Product Brief phase: {e}", flush=True)
                                    break

                            # Only proceed to Backlog if Brief was approved
                            if decision in ['approve', 'a'] or (decision not in ['cancel', 'c'] and brief_attempt <= max_brief_attempts):
                                # ========== EPICS & STORIES PHASE (with revision loop) ==========
                                backlog_attempt = 0
                                max_backlog_attempts = 3
                                revision_feedback = ""

                                while backlog_attempt < max_backlog_attempts:
                                    backlog_attempt += 1
                                    print(f"\n📋 Creating Epics & Stories (Attempt {backlog_attempt}/{max_backlog_attempts})...", flush=True)
                                    print("-" * 70, flush=True)

                                    try:
                                        backlog_text, needs_revision, validation_report = ba_crew.run_backlog_phase(revision_feedback)

                                        # Reload state
                                        ba_crew.state_manager = ba_crew.state_manager.__class__(ba_crew.state_manager.state_file, new_session=False)
                                        ba_crew.state_tool.state_manager = ba_crew.state_manager
                                        ba_crew.solution_tool.state_manager = ba_crew.state_manager
                                        ba_crew.documentation_tool.state_manager = ba_crew.state_manager

                                        print("\n" + "=" * 70, flush=True)
                                        print("📋 PRODUCT BACKLOG", flush=True)
                                        print("=" * 70, flush=True)
                                        print(backlog_text, flush=True)

                                        print("\n" + "=" * 70, flush=True)
                                        print("✔️ VALIDATION REPORT", flush=True)
                                        print("=" * 70, flush=True)
                                        print(validation_report, flush=True)

                                        # Ask user for decision
                                        print("\n" + "=" * 70, flush=True)
                                        decision = input("Approve Epics & Stories? (approve/revise/cancel): ").strip().lower()

                                        if decision in ['approve', 'a']:
                                            print("\n✅ Epics & Stories approved!", flush=True)
                                            break
                                        elif decision in ['cancel', 'c']:
                                            print("\n❌ Backlog creation cancelled.", flush=True)
                                            break
                                        elif decision in ['revise', 'r']:
                                            if backlog_attempt >= max_backlog_attempts:
                                                print(f"\n⚠️ Maximum revision attempts ({max_backlog_attempts}) reached.", flush=True)
                                                break
                                            revision_feedback = input("\nWhat needs to be revised? (be specific): ").strip()
                                            if not revision_feedback:
                                                print("\n⚠️ No feedback provided. Using previous version.", flush=True)
                                                break
                                            print(f"\n🔄 Revising Epics & Stories based on feedback...", flush=True)
                                        else:
                                            print("\n⚠️ Invalid input. Treating as 'approve'.", flush=True)
                                            break

                                    except Exception as e:
                                        print(f"\n❌ Error during Backlog phase: {e}", flush=True)
                                        break

                        # End session after documentation phase
                        print("\n" + "=" * 70, flush=True)
                        print("✅ Session completed successfully!", flush=True)
                        print("All data saved to conversation_state.json", flush=True)
                        print("=" * 70, flush=True)
                        break

                    except Exception as e:
                        print(f"\n❌ Error during solution phase: {e}", flush=True)
                        print("Requirements have been saved. You can continue or exit.", flush=True)
                        continue_input = input("\nContinue conversation or exit? (continue/exit): ").strip().lower()
                        if continue_input in ['exit', 'quit', 'e']:
                            break
                        else:
                            print("\nContinuing conversation in Analysis phase...", flush=True)

            except Exception as e:
                print(f"\n❌ Error during conversation: {e}")
                print("Please try again or type 'quit' to exit.")

    except Exception as e:
        raise Exception(f"An error occurred while running the BA system: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs",
        'current_year': str(datetime.now().year)
    }
    try:
        MyProject().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        MyProject().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }

    try:
        MyProject().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

def run_with_trigger():
    """
    Run the crew with trigger payload.
    """
    import json

    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided. Please provide JSON payload as argument.")

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument")

    inputs = {
        "crewai_trigger_payload": trigger_payload,
        "topic": "",
        "current_year": ""
    }

    try:
        result = MyProject().crew().kickoff(inputs=inputs)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew with trigger: {e}")
