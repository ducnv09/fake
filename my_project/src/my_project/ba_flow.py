"""
Business Analyst Flow - Workflow with Pydantic State Management
Replaces manual JSON state management with Pydantic-based state
"""

import os
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, task
from .flow_state import BAFlowState
from .tools.state_tool import FlowStateTool
from .tools.solution_tool import FlowSolutionTool
from .tools.documentation_tool import FlowDocumentationTool
from .tools.user_interaction_tool import FlowUserInteractionTool
from .models.solution_models import FlowsOutput
from .models.documentation_models import ProductBriefData, BacklogOutput


@CrewBase
class BAFlow():
    """
    Business Analyst Flow for requirements gathering, solution design, and documentation
    Uses Pydantic-based state management (BAFlowState)

    Methods are called directly from main.py for interactive conversation mode
    """

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self):
        """Initialize Flow with Pydantic state"""
        self.state = BAFlowState()
        self._state_tool = None
        self._solution_tool = None
        self._documentation_tool = None
        self._user_interaction_tool = None

        # Cache agents to avoid recreation
        self._cached_agents = {}

        # Load model configurations from environment
        self.strong_model = os.getenv("STRONG_MODEL", "openai/gpt-4.1")
        self.light_model = os.getenv("LIGHT_MODEL", "openai/gpt-4.1")

    # ==================== TOOLS ====================
    @property
    def state_tool(self):
        """Tool for managing requirements and analysis state"""
        if self._state_tool is None:
            self._state_tool = FlowStateTool(self)
        return self._state_tool

    @property
    def solution_tool(self):
        """Tool for managing solution components"""
        if self._solution_tool is None:
            self._solution_tool = FlowSolutionTool(self)
        return self._solution_tool

    @property
    def documentation_tool(self):
        """Tool for managing documentation (Product Brief, Epics, Stories)"""
        if self._documentation_tool is None:
            self._documentation_tool = FlowDocumentationTool(self)
        return self._documentation_tool

    @property
    def user_interaction_tool(self):
        """Tool for presenting options and getting user choices"""
        if self._user_interaction_tool is None:
            self._user_interaction_tool = FlowUserInteractionTool(self)
        return self._user_interaction_tool

    # ==================== AGENTS ====================
    @agent
    def business_analyst(self) -> Agent:
        if 'business_analyst' not in self._cached_agents:
            self._cached_agents['business_analyst'] = Agent(
                config=self.agents_config['business_analyst'],
                verbose=True,
                tools=[],  # No tools - BA will return structured output instead
                allow_delegation=False,
                max_iter=15,
                llm=self.strong_model  # Complex task: gathering requirements
            )
        return self._cached_agents['business_analyst']

    @agent
    def phase_coordinator(self) -> Agent:
        if 'phase_coordinator' not in self._cached_agents:
            self._cached_agents['phase_coordinator'] = Agent(
                config=self.agents_config['phase_coordinator'],
                verbose=False,
                tools=[self.state_tool],
                llm=self.light_model  # Simple task: phase evaluation
            )
        return self._cached_agents['phase_coordinator']

    @agent
    def solution_designer(self) -> Agent:
        return Agent(
            config=self.agents_config['solution_designer'],
            verbose=True,
            tools=[],  # Removed solution_tool to enable Pydantic bulk output
            llm=self.strong_model  # Complex task: designing solutions
        )

    @agent
    def solution_validator(self) -> Agent:
        return Agent(
            config=self.agents_config['solution_validator'],
            verbose=True,
            tools=[self.solution_tool],
            llm=self.light_model  # Simple task: validation
        )

    @agent
    def product_brief_writer(self) -> Agent:
        if 'product_brief_writer' not in self._cached_agents:
            self._cached_agents['product_brief_writer'] = Agent(
                config=self.agents_config['product_brief_writer'],
                verbose=True,
                tools=[],  # No tools - outputs Pydantic model instead
                llm=self.strong_model  # Complex task: writing Product Brief
            )
        return self._cached_agents['product_brief_writer']

    @agent
    def brief_reviewer(self) -> Agent:
        if 'brief_reviewer' not in self._cached_agents:
            self._cached_agents['brief_reviewer'] = Agent(
                config=self.agents_config['brief_reviewer'],
                verbose=True,
                tools=[self.documentation_tool],  # Still needs tool to read brief
                llm=self.light_model  # Simple task: review
            )
        return self._cached_agents['brief_reviewer']

    @agent
    def epic_story_writer(self) -> Agent:
        if 'epic_story_writer' not in self._cached_agents:
            self._cached_agents['epic_story_writer'] = Agent(
                config=self.agents_config['epic_story_writer'],
                verbose=True,
                tools=[],  # No tools - outputs Pydantic model instead
                llm=self.strong_model  # Complex task: writing Epics & Stories
            )
        return self._cached_agents['epic_story_writer']

    @agent
    def backlog_validator(self) -> Agent:
        if 'backlog_validator' not in self._cached_agents:
            self._cached_agents['backlog_validator'] = Agent(
                config=self.agents_config['backlog_validator'],
                verbose=True,
                tools=[self.documentation_tool],
                llm=self.light_model  # Simple task: validation
            )
        return self._cached_agents['backlog_validator']

    # ==================== TASKS ====================
    @task
    def analysis_task(self) -> Task:
        return Task(config=self.tasks_config['analysis_task'])

    @task
    def phase_evaluation_task(self) -> Task:
        return Task(config=self.tasks_config['phase_evaluation_task'])

    @task
    def solution_design_flows_task(self) -> Task:
        return Task(
            config=self.tasks_config['solution_design_flows_task'],
            output_pydantic=FlowsOutput
        )

    @task
    def solution_validation_task(self) -> Task:
        return Task(config=self.tasks_config['solution_validation_task'])

    @task
    def solution_phase_evaluation_task(self) -> Task:
        return Task(config=self.tasks_config['solution_phase_evaluation_task'])

    @task
    def product_brief_creation_task(self) -> Task:
        return Task(
            config=self.tasks_config['product_brief_creation_task'],
            output_pydantic=ProductBriefData
        )

    @task
    def product_brief_review_task(self) -> Task:
        return Task(config=self.tasks_config['product_brief_review_task'])

    @task
    def epic_story_creation_task(self) -> Task:
        return Task(
            config=self.tasks_config['epic_story_creation_task'],
            output_pydantic=BacklogOutput
        )

    @task
    def backlog_validation_task(self) -> Task:
        return Task(config=self.tasks_config['backlog_validation_task'])

    # ==================== FLOW METHODS ====================

    def analysis_phase(self):
        """
        Phase 1: Requirements gathering through conversation
        Runs BA and Coordinator to collect and evaluate requirements
        Called directly from main.py for each user message
        """
        # Get user input
        user_message = self.state.conversation_history[-1]['content'] if self.state.conversation_history else ""

        # Prepare context
        conversation_context = self._get_conversation_summary()
        requirements_summary = self.state.get_all_requirements_text()

        # Count turns
        turn_count = len([msg for msg in self.state.conversation_history if msg["role"] == "user"])
        total_reqs = sum(len(v) for v in self.state.requirements.values())

        # Create analysis crew
        analysis_crew = Crew(
            agents=[self.business_analyst(), self.phase_coordinator()],
            tasks=[self.analysis_task(), self.phase_evaluation_task()],
            process=Process.sequential,
            verbose=False
        )

        # Run crew
        result = analysis_crew.kickoff(inputs={
            'user_message': user_message,
            'conversation_context': conversation_context,
            'requirements_summary': requirements_summary,
            'turn_count': turn_count,
            'total_requirements': total_reqs
        })

        # Extract results
        ba_response = str(result.tasks_output[0].raw)
        phase_evaluation = str(result.tasks_output[1].raw)

        # DEBUG: Print raw BA response to see format
        print(f"\n[RAW BA RESPONSE]:")
        print(ba_response)
        print(f"[END RAW BA RESPONSE]\n")

        # Parse and save requirements from BA response
        parsed_reqs = self._parse_requirements_from_response(ba_response)
        print(f"[PARSE DEBUG] Found {len(parsed_reqs)} requirements")
        if parsed_reqs:
            print(f"[PARSE DEBUG] Parsed {len(parsed_reqs)} requirements from BA output")
            for req in parsed_reqs:
                success = self.state.add_requirement(req['category'], req['content'])
                if success:
                    print(f"[PARSE DEBUG] Saved: {req['category']} - {req['content'][:50]}...")
        else:
            print("[PARSE DEBUG] No requirements found in BA response - check format!")

        # Extract user response (the conversational part)
        user_response = self._extract_user_response(ba_response)

        # Save user response to conversation
        self.state.add_message("assistant", user_response)

        # DEBUG: Print state after crew execution
        total_after = sum(len(v) for v in self.state.requirements.values())
        print(f"\n[DEBUG] Requirements count after crew execution: {total_after}")
        print(f"[DEBUG] Details: problem_goals={len(self.state.requirements['problem_goals'])}, users_stakeholders={len(self.state.requirements['users_stakeholders'])}, features_scope={len(self.state.requirements['features_scope'])}")

        return {
            "ba_response": user_response,  # Return the clean conversational response
            "phase_evaluation": phase_evaluation
        }

    def check_analysis_complete(self, phase_evaluation: str = ""):
        """
        Check if analysis phase is complete based on Phase Coordinator's decision
        Returns: 'analysis_complete' or 'analysis_continue'
        """
        # Parse Phase Coordinator's decision
        is_ready = "DECISION: READY" in phase_evaluation or "DECISION:READY" in phase_evaluation

        # Extract reasoning from phase_evaluation
        reasoning = ""
        if "REASONING:" in phase_evaluation:
            lines = phase_evaluation.split("\n")
            for i, line in enumerate(lines):
                if "REASONING:" in line:
                    # Get reasoning text (may span multiple lines)
                    reasoning = line.split("REASONING:", 1)[1].strip()
                    # Check if reasoning continues on next lines
                    for j in range(i+1, len(lines)):
                        next_line = lines[j].strip()
                        if next_line and not next_line.startswith("NEXT_STEPS:") and not next_line.startswith("DECISION:"):
                            reasoning += " " + next_line
                        else:
                            break
                    break

        if is_ready:
            print(f"\n✅ Phân tích hoàn tất!")
            if reasoning:
                print(f"   Lý do: {reasoning}")
            print(f"\n   💡 Gõ 'done' để chuyển sang phase Solution Design")
            return "analysis_complete"
        else:
            print(f"\n⏳ Đang thu thập thông tin...")
            if reasoning:
                print(f"   {reasoning}")
            return "analysis_continue"

    def solution_phase(self, revision_feedback: str = ""):
        """
        Phase 3: Solution Design
        Runs Designer and Validator to create solution architecture (business flows only)
        NOW RUNS AFTER BRIEF - designs HOW to implement the Product Brief
        Called directly from main.py after brief is approved
        """
        # Transition phase (only on first run)
        if not revision_feedback:
            self.state.transition_to_phase("solution", "Product Brief approved, designing solution")

        # Get requirements and product brief
        requirements_summary = self.state.get_all_requirements_text()
        product_brief = self.state.get_product_brief_text()

        # Get current solution if exists (for refinement context)
        current_solution = ""
        if revision_feedback and self.state.solution.get('business_flows'):
            current_solution = self.state.get_solution_text()
            # Clear flows AFTER capturing current state for refinement context
            self.state.solution['business_flows'] = []

        # ===== Design Business Flows =====
        print("\n🔄 Designing business flows...")
        solution_summary = self.state.get_solution_text() if not revision_feedback else ""

        flows_crew = Crew(
            agents=[self.solution_designer()],
            tasks=[self.solution_design_flows_task()],
            process=Process.sequential,
            verbose=False
        )

        flows_result = flows_crew.kickoff(inputs={
            'requirements_summary': requirements_summary,
            'product_brief': product_brief,
            'solution_summary': solution_summary,
            'revision_feedback': revision_feedback if revision_feedback else "None",
            'current_solution': current_solution if current_solution else "None"
        })

        # Get Pydantic output directly from task result
        flows_output_obj: FlowsOutput = flows_result.pydantic

        # Add all flows from Pydantic model to state
        for flow in flows_output_obj.business_flows:
            self.state.solution["business_flows"].append(flow.model_dump())

        print(f"✅ Flows designed: {len(flows_output_obj.business_flows)} flows added")
        flows_output = str(flows_result.tasks_output[0].raw)

        # ===== Validate Solution =====
        print("\n🔍 Validating solution...")
        solution_summary = self.state.get_solution_text()

        validation_crew = Crew(
            agents=[self.solution_validator(), self.phase_coordinator()],
            tasks=[self.solution_validation_task(), self.solution_phase_evaluation_task()],
            process=Process.sequential,
            verbose=False
        )

        validation_result = validation_crew.kickoff(inputs={
            'requirements_summary': requirements_summary,
            'product_brief': product_brief,
            'solution_summary': solution_summary,
            'validation_results': ""
        })

        # Combine outputs
        design_summary = flows_output
        validation_report = str(validation_result.tasks_output[0].raw)
        phase_evaluation = str(validation_result.tasks_output[1].raw)

        # Store phase_evaluation temporarily for routing
        self._last_phase_evaluation = phase_evaluation

        return {
            "design_summary": design_summary,
            "validation_report": validation_report,
            "phase_evaluation": phase_evaluation
        }

    def check_solution_complete(self):
        """
        Check if solution phase is complete
        Returns: 'solution_complete' or 'solution_incomplete'
        """
        phase_eval = getattr(self, '_last_phase_evaluation', "")

        if "DECISION: READY" in phase_eval or "DECISION:READY" in phase_eval:
            print("\n✅ Solution design complete")
            return "solution_complete"
        else:
            print("\n⚠️ Solution needs more work")
            return "solution_incomplete"

    def brief_phase(self):
        """
        Phase 2: Product Brief creation
        Runs Brief Writer and Reviewer to create Product Brief
        Called from main.py AFTER analysis is complete, BEFORE solution design
        Returns brief for user approval BEFORE designing solution
        """
        # Transition phase
        self.state.transition_to_phase("brief", "Analysis complete, creating Product Brief")

        # Create Product Brief
        brief_result = self._run_product_brief_phase()

        return brief_result

    def documentation_phase_backlog(self):
        """
        Phase 3B: Epics & Stories creation
        Runs Epic/Story Writer and Validator to create Product Backlog
        Called from main.py AFTER brief is approved by user
        """
        # Create Epics & Stories
        backlog_result = self._run_backlog_phase()

        return backlog_result

    def documentation_phase(self):
        """
        LEGACY: Phase 3 combined (Product Brief + Epics/Stories)
        Keep for backward compatibility but not recommended
        Prefer using documentation_phase_brief() then documentation_phase_backlog()
        """
        # Transition phase
        self.state.transition_to_phase("documentation", "Solution complete, moving to documentation")

        # Sub-phase 1: Product Brief
        brief_result = self._run_product_brief_phase()

        # Sub-phase 2: Epics & Stories
        backlog_result = self._run_backlog_phase()

        return {
            "product_brief": brief_result,
            "backlog": backlog_result
        }

    def _run_product_brief_phase(self, revision_feedback: str = "") -> dict:
        """
        Create Product Brief (internal method)
        NOW RUNS BEFORE SOLUTION - only uses requirements, not solution
        Uses Pydantic output instead of tool calls
        """
        print("\n📝 Creating Product Brief...")

        requirements_summary = self.state.get_all_requirements_text()

        # Get current brief if exists (for refinement context)
        current_brief = ""
        if revision_feedback and self.state.documentation.get('product_brief'):
            current_brief = self.state.get_product_brief_text()

        # Create brief crew
        brief_crew = Crew(
            agents=[self.product_brief_writer(), self.brief_reviewer()],
            tasks=[self.product_brief_creation_task(), self.product_brief_review_task()],
            process=Process.sequential,
            verbose=True
        )

        # Run crew
        result = brief_crew.kickoff(inputs={
            'requirements_summary': requirements_summary,
            'revision_feedback': revision_feedback if revision_feedback else "None",
            'current_brief': current_brief if current_brief else "None"
        })

        # Get Pydantic output from FIRST task (Product Brief Writer)
        brief_task_output = result.tasks_output[0]
        brief_data: ProductBriefData = brief_task_output.pydantic

        # Check if Pydantic output exists
        if brief_data is None:
            print("⚠️ Warning: No Pydantic output from Product Brief Writer")
            print("⚠️ Brief may have been saved by Reviewer instead")
        else:
            # Save to state using documentation tool
            self.documentation_tool._run(
                action='save_brief',
                data=brief_data.model_dump_json()
            )
            print(f"✅ Product Brief created and saved")

        # Extract results
        review_report = str(result.tasks_output[1].raw)
        brief_text = self.state.get_product_brief_text()

        needs_revision = "REVIEW STATUS: NEEDS_REVISION" in review_report or "NEEDS_REVISION" in review_report

        return {
            "brief_text": brief_text,
            "needs_revision": needs_revision,
            "review_report": review_report
        }

    def _run_backlog_phase(self, revision_feedback: str = "") -> dict:
        """
        Create Epics & Stories (internal method)
        Uses Pydantic output instead of tool calls
        """
        print("\n📋 Creating Epics & Stories...")

        solution_summary = self.state.get_solution_text()
        product_brief = self.state.get_product_brief_text()

        # Get current backlog if exists (for refinement context)
        current_backlog = ""
        if revision_feedback and (self.state.documentation.get('epics') or self.state.documentation.get('stories')):
            current_backlog = self.state.get_backlog_text()
            # Clear epics and stories AFTER capturing current state for refinement context
            self.state.documentation['epics'] = []
            self.state.documentation['stories'] = []

        # Create backlog crew
        backlog_crew = Crew(
            agents=[self.epic_story_writer(), self.backlog_validator()],
            tasks=[self.epic_story_creation_task(), self.backlog_validation_task()],
            process=Process.sequential,
            verbose=True
        )

        # Run crew
        result = backlog_crew.kickoff(inputs={
            'solution_summary': solution_summary,
            'product_brief': product_brief,
            'revision_feedback': revision_feedback if revision_feedback else "None",
            'current_backlog': current_backlog if current_backlog else "None"
        })

        # Get Pydantic output from FIRST task (Epic & Story Writer)
        backlog_task_output = result.tasks_output[0]
        backlog_data: BacklogOutput = backlog_task_output.pydantic

        # Check if Pydantic output exists
        if backlog_data is None:
            print("⚠️ Warning: No Pydantic output from Epic & Story Writer")
        else:
            # Save epics and stories to state using documentation tool
            for epic in backlog_data.epics:
                self.documentation_tool._run(
                    action='add_epic',
                    data=epic.model_dump_json()
                )

            for story in backlog_data.stories:
                self.documentation_tool._run(
                    action='add_story',
                    data=story.model_dump_json()
                )

            print(f"✅ Backlog created: {len(backlog_data.epics)} epics, {len(backlog_data.stories)} stories")

        # Extract results
        validation_report = str(result.tasks_output[1].raw)
        backlog_text = self.state.get_backlog_text()

        needs_revision = "VALIDATION STATUS: INCOMPLETE" in validation_report or "INCOMPLETE" in validation_report

        return {
            "backlog_text": backlog_text,
            "needs_revision": needs_revision,
            "validation_report": validation_report
        }

    # ==================== HELPER METHODS ====================

    def _parse_requirements_from_response(self, ba_response: str) -> list:
        """
        Parse requirements from BA's structured output
        Expected format:
        === EXTRACTED REQUIREMENTS ===
        PROBLEM_GOALS:
        - requirement 1
        - requirement 2

        USERS_STAKEHOLDERS:
        - requirement 3

        FEATURES_SCOPE:
        - requirement 4
        === END REQUIREMENTS ===
        """
        requirements = []

        # Find the requirements section
        if "=== EXTRACTED REQUIREMENTS ===" not in ba_response:
            return requirements

        start_idx = ba_response.find("=== EXTRACTED REQUIREMENTS ===")

        # Try both formats: with and without spaces
        end_idx = ba_response.find("=== END REQUIREMENTS ===")
        if end_idx == -1:
            end_idx = ba_response.find("===END REQUIREMENTS===")

        if start_idx == -1 or end_idx == -1:
            return requirements

        req_section = ba_response[start_idx:end_idx]

        # Parse each category
        current_category = None
        category_map = {
            "PROBLEM_GOALS": "problem_goals",
            "USERS_STAKEHOLDERS": "users_stakeholders",
            "FEATURES_SCOPE": "features_scope"
        }

        for line in req_section.split('\n'):
            line = line.strip()

            # Check if this is a category header (with or without colon)
            line_without_colon = line.rstrip(':')
            if line_without_colon in category_map:
                current_category = category_map[line_without_colon]
                continue

            # Check if this is a requirement (starts with -)
            if line.startswith('-') and current_category:
                content = line[1:].strip()  # Remove the leading '-'
                if content:
                    requirements.append({
                        'category': current_category,
                        'content': content
                    })

        return requirements

    def _extract_user_response(self, ba_response: str) -> str:
        """
        Extract the conversational response part from BA output
        Expected format:
        === USER RESPONSE ===
        [response text]
        === END RESPONSE ===
        """
        # Find the response section
        if "=== USER RESPONSE ===" not in ba_response:
            # Fallback: return everything after requirements section
            # Try both formats: with and without spaces
            end_idx = ba_response.find("=== END REQUIREMENTS ===")
            if end_idx == -1:
                end_idx = ba_response.find("===END REQUIREMENTS===")

            if end_idx != -1:
                marker_len = len("=== END REQUIREMENTS ===") if "=== END REQUIREMENTS ===" in ba_response else len("===END REQUIREMENTS===")
                return ba_response[end_idx + marker_len:].strip()
            return ba_response.strip()

        start_idx = ba_response.find("=== USER RESPONSE ===")
        end_idx = ba_response.find("=== END RESPONSE ===")

        if start_idx == -1:
            return ba_response.strip()

        if end_idx == -1:
            # No end marker, take everything after start
            return ba_response[start_idx + len("=== USER RESPONSE ==="):].strip()

        response_text = ba_response[start_idx + len("=== USER RESPONSE ==="):end_idx].strip()
        return response_text

    def _get_conversation_summary(self) -> str:
        """Get conversation summary for context"""
        history_count = len(self.state.conversation_history)
        reqs = self.state.requirements

        summary = f"""
Current Phase: {self.state.current_phase}
Conversation Messages: {history_count}

Requirements Collected:
- Problem & Goals: {len(reqs["problem_goals"])} items
- Users & Stakeholders: {len(reqs["users_stakeholders"])} items
- Features & Scope: {len(reqs["features_scope"])} items

Total Requirements: {sum(len(v) for v in reqs.values())}
"""
        return summary.strip()

    def add_user_message(self, message: str):
        """Add user message to state (convenience method)"""
        self.state.add_message("user", message)
