#!/usr/bin/env python
"""
Business Analyst Flow - Main Entry Point
Interactive conversation mode using CrewAI Flow with built-in state management
"""

import sys
import warnings
from my_project.ba_flow import BAFlow

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def display_pending_question(pending_question):
    """Display a pending user question with options"""
    print("\n" + "=" * 70)
    print("🤔 USER INPUT NEEDED")
    print("=" * 70)
    print(f"\nQuestion: {pending_question['question']}")
    print(f"Context: {pending_question['context']}")
    print("\nOptions:")

    options = pending_question['options']
    for i, opt in enumerate(options, 1):
        print(f"\n{i}. {opt['label']}")
        if opt.get('description'):
            print(f"   → {opt['description']}")

    print("\n" + "-" * 70)
    return options


def get_user_choice_input(options):
    """Get user's choice from the options"""
    while True:
        try:
            choice_input = input(f"\nYour choice (1-{len(options)}): ").strip()

            if not choice_input:
                continue

            choice_num = int(choice_input)

            if 1 <= choice_num <= len(options):
                selected = options[choice_num - 1]
                return selected
            else:
                print(f"❌ Please enter a number between 1 and {len(options)}")

        except ValueError:
            print("❌ Please enter a valid number")
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user")
            return None


def request_approval(title, content, phase):
    """Request user approval for a phase output"""
    print("\n" + "=" * 70)
    print(f"📋 {title} - PREVIEW")
    print("=" * 70)
    print(content)

    print("\n" + "=" * 70)
    print("Do you approve this? (y/n/refine)")
    print("  y     - Approve and continue")
    print("  n     - Reject and skip")
    print("  refine - Request changes")
    print("=" * 70)

    while True:
        response = input("\nYour response: ").strip().lower()

        if response in ['y', 'yes']:
            return 'approved', ''
        elif response in ['n', 'no']:
            return 'rejected', ''
        elif response in ['refine', 'r']:
            feedback = input("\n What would you like to change? ").strip()
            if feedback:
                return 'refine', feedback
            else:
                print("❌ Please provide feedback for refinement")
        else:
            print("❌ Please enter 'y', 'n', or 'refine'")


def display_progress(flow):
    """Display current progress"""
    progress = flow.state.get_progress_summary()

    print("\n" + "=" * 70)
    print("📊 PROGRESS SUMMARY")
    print("=" * 70)
    print(f"\nCurrent Phase: {progress['current_phase'].upper()}")

    print("\n📋 Analysis Phase:")
    print(f"  {'✅' if progress['analysis']['complete'] else '⏳'} Requirements: {progress['analysis']['requirements_count']} collected")

    print("\n🎨 Solution Phase:")
    print(f"  {'✅' if progress['solution']['components_count'] > 0 else '⏳'} Components: {progress['solution']['components_count']} designed")

    print("\n📄 Documentation Phase:")
    brief_status = '✅' if progress['documentation']['brief_created'] else '⏳'
    print(f"  {brief_status} Product Brief: {'Created' if progress['documentation']['brief_created'] else 'Pending'}")
    print(f"  {'✅' if progress['documentation']['epics_count'] > 0 else '⏳'} Epics: {progress['documentation']['epics_count']}")
    print(f"  {'✅' if progress['documentation']['stories_count'] > 0 else '⏳'} Stories: {progress['documentation']['stories_count']}")

    if progress['user_interactions']['choices_made'] > 0:
        print(f"\n🤝 User Interactions: {progress['user_interactions']['choices_made']} choices made")

    if progress['user_interactions']['pending_question']:
        print("\n⚠️ There is a pending question waiting for your response!")

    print("=" * 70)


def run():
    """
    Run the Business Analyst Flow in interactive mode
    """
    print("=" * 70, flush=True)
    print("BUSINESS ANALYST - Requirements Gathering System (Flow Mode)", flush=True)
    print("=" * 70, flush=True)
    print("\nWelcome! I'm your Business Analyst assistant.", flush=True)
    print("I'll help you gather requirements for your software project.", flush=True)
    print("\nPhase: ANALYSIS", flush=True)
    print("Focus: Understanding your problem, users, and desired features", flush=True)
    print("\nFlow: Analysis → Product Brief → Solution Design → Product Backlog", flush=True)
    print("\nCommands:", flush=True)
    print("  'status'   - See collected requirements", flush=True)
    print("  'progress' - See overall progress", flush=True)
    print("  'done'     - Move to Product Brief creation", flush=True)
    print("  'quit'     - End session", flush=True)
    print("=" * 70, flush=True)
    print(flush=True)

    try:
        # Initialize Flow with state
        print("Initializing BA Flow (this may take a moment)...", flush=True)
        flow = BAFlow()
        print("BA Flow ready!", flush=True)

        # Start conversation loop for analysis phase
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
                print("Session ended.")
                print("=" * 70)
                print("\n📋 FINAL REQUIREMENTS SUMMARY:")
                print(flow.state.get_all_requirements_text())
                break

            # Check for status command
            if user_input.lower() == 'status':
                print("\n" + "=" * 70)
                print("📊 CURRENT STATUS:")
                print("=" * 70)
                print(flow._get_conversation_summary())
                print("\n📋 COLLECTED REQUIREMENTS:")
                print(flow.state.get_all_requirements_text())
                continue

            # Check for progress command
            if user_input.lower() == 'progress':
                display_progress(flow)
                continue

            # Check if user wants to proceed to solution phase
            if user_input.lower() == 'done':
                print("\n" + "=" * 70)
                print("✅ Analysis complete, moving to PRODUCT BRIEF creation...")
                print("=" * 70)

                try:
                    # Add a final marker message
                    flow.state.add_message("user", "[Analysis phase completed by user]")

                    # ===== PHASE 2: Create Product Brief =====
                    print("\n📝 Phase 2: Creating Product Brief...")
                    print("This may take a few moments...")
                    print("-" * 70)

                    brief_result = flow.brief_phase()

                    # Display and approve Product Brief
                    brief_text = brief_result['brief_text']

                    print("\n" + "=" * 70)
                    print("📊 BRIEF REVIEW")
                    print("=" * 70)
                    print(brief_result['review_report'])

                    brief_approval_status, brief_feedback = request_approval(
                        "PRODUCT BRIEF",
                        brief_text,
                        "brief_approved"
                    )

                    if brief_approval_status == 'approved':
                        flow.state.record_approval("brief_approved", True, "")
                        print("\n✅ Product Brief approved!")
                    elif brief_approval_status == 'refine':
                        flow.state.record_approval("brief_approved", False, brief_feedback)
                        print(f"\n📝 Refinement requested: {brief_feedback}")
                        print("⚠️ Note: Automatic refinement not yet implemented.")
                    else:
                        flow.state.record_approval("brief_approved", False, "User rejected")
                        print("\n⚠️ Product Brief rejected.")

                    # Only proceed to Solution if Brief approved
                    if brief_approval_status == 'approved':
                        # ===== PHASE 3: Design Solution =====
                        print("\n" + "=" * 70)
                        print("🚀 Moving to SOLUTION DESIGN phase...")
                        print("=" * 70)

                        print("\n🎨 Solution Designer is working...")
                        print("This may take a few moments...")
                        print("-" * 70)

                        result = flow.solution_phase()

                        # Check if there's a pending user question from solution phase
                        if flow.state.pending_user_question:
                            pending_q = flow.state.pending_user_question
                            options = display_pending_question(pending_q)

                            selected = get_user_choice_input(options)

                            if selected:
                                flow.state.add_user_choice(
                                    context=pending_q['context'],
                                    question=pending_q['question'],
                                    selected_label=selected['label'],
                                    selected_value=selected['value']
                                )
                                print(f"\n✅ Choice recorded: {selected['label']}")

                                # Re-run solution phase with user choice
                                print("\n🎨 Applying your choice...")
                                result = flow.solution_phase()

                        # Display solution results
                        print("\n" + "=" * 70)
                        print("✅ SOLUTION PHASE COMPLETE!")
                        print("=" * 70)

                        print("\n📐 Solution Design Summary:")
                        print(result['design_summary'])

                        print("\n✔️ Validation Report:")
                        print(result['validation_report'])

                        print("\n📊 Phase Evaluation:")
                        print(result['phase_evaluation'])

                        # Request user approval for solution
                        solution_preview = flow.state.get_solution_text()
                        solution_approval_status, solution_feedback = request_approval(
                            "SOLUTION DESIGN",
                            solution_preview,
                            "solution_approved"
                        )

                        if solution_approval_status == 'approved':
                            flow.state.record_approval("solution_approved", True, "")
                            print("\n✅ Solution approved!")
                        elif solution_approval_status == 'refine':
                            flow.state.record_approval("solution_approved", False, solution_feedback)
                            print(f"\n📝 Refinement requested: {solution_feedback}")
                            print("⚠️ Note: Automatic refinement not yet implemented. Continuing with current solution.")
                        else:
                            flow.state.record_approval("solution_approved", False, "User rejected")
                            print("\n⚠️ Solution rejected. Continuing anyway.")

                        # Only proceed to Backlog if Solution approved
                        if solution_approval_status == 'approved':
                            # ===== PHASE 4: Create Epics & Stories =====
                            print("\n" + "=" * 70)
                            print("📋 Moving to PRODUCT BACKLOG creation...")
                            print("=" * 70)

                            print("\n📋 Creating Epics & Stories...")
                            print("This may take a few moments...")
                            print("-" * 70)

                            backlog_result = flow.documentation_phase_backlog()

                            # Display and approve Backlog
                            backlog_text = backlog_result['backlog_text']

                            print("\n" + "=" * 70)
                            print("✔️ BACKLOG VALIDATION")
                            print("=" * 70)
                            print(backlog_result['validation_report'])

                            backlog_approval_status, backlog_feedback = request_approval(
                                "PRODUCT BACKLOG",
                                backlog_text,
                                "backlog_approved"
                            )

                            if backlog_approval_status == 'approved':
                                flow.state.record_approval("backlog_approved", True, "")
                                print("\n✅ Product Backlog approved!")
                            elif backlog_approval_status == 'refine':
                                flow.state.record_approval("backlog_approved", False, backlog_feedback)
                                print(f"\n📝 Refinement requested: {backlog_feedback}")
                                print("⚠️ Note: Automatic refinement not yet implemented.")
                            else:
                                flow.state.record_approval("backlog_approved", False, "User rejected")
                                print("\n⚠️ Product Backlog rejected.")
                        else:
                            print("\n⚠️ Skipping Backlog creation because Solution was not approved.")
                    else:
                        print("\n⚠️ Skipping Solution and Backlog phases because Brief was not approved.")

                    # End session
                    print("\n" + "=" * 70)
                    print("✅ Session completed successfully!")
                    print("=" * 70)
                    break

                except Exception as e:
                    print(f"\n❌ Error during brief/solution/backlog phases: {e}")
                    import traceback
                    traceback.print_exc()
                    break

            # Process user message through BA Flow (analysis phase only)
            turn_count += 1
            print(f"\n🤖 BA Agent is thinking... (Turn {turn_count})")
            print("-" * 70)

            try:
                # Add user message to state
                flow.state.add_message("user", user_input)

                # Run analysis phase
                result = flow.analysis_phase()

                # Display BA response
                ba_response = result.get('ba_response', '')
                print(f"\n💼 Business Analyst:\n{ba_response}")

                # Check if there's a pending user question
                if flow.state.pending_user_question:
                    pending_q = flow.state.pending_user_question
                    options = display_pending_question(pending_q)

                    selected = get_user_choice_input(options)

                    if selected:
                        # Record user choice
                        flow.state.add_user_choice(
                            context=pending_q['context'],
                            question=pending_q['question'],
                            selected_label=selected['label'],
                            selected_value=selected['value']
                        )
                        print(f"\n✅ Choice recorded: {selected['label']}")
                    else:
                        print("\n⚠️ Choice cancelled")

                # Check if analysis is automatically complete
                phase_eval = result.get('phase_evaluation', '')
                should_transition = flow.check_analysis_complete(phase_eval)

            except Exception as e:
                print(f"\n❌ Error during conversation: {e}")
                import traceback
                traceback.print_exc()
                print("Please try again or type 'quit' to exit.")

    except Exception as e:
        import traceback
        print(f"\n❌ An error occurred while running the BA Flow: {e}")
        traceback.print_exc()


def train():
    """
    Train the flow (not implemented for Flow architecture)
    """
    print("Training is not implemented for Flow architecture.")
    print("Please use the standard run() mode.")


def replay():
    """
    Replay the flow (not implemented for Flow architecture)
    """
    print("Replay is not implemented for Flow architecture.")
    print("Please use the standard run() mode.")


def test():
    """
    Test the flow (not implemented for Flow architecture)
    """
    print("Testing is not implemented for Flow architecture.")
    print("Please use the standard run() mode.")


if __name__ == "__main__":
    run()
