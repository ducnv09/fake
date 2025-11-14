from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, before_kickoff
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List, Optional
from .state_manager import ConversationState
from .tools.state_tool import StateTool
from .tools.solution_tool import SolutionTool
from .tools.documentation_tool import DocumentationTool

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

_shared_state_manager = None
_shared_new_session = False

@CrewBase
class MyProject():
    """Business Analyst crew for requirements gathering"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @property
    def state_manager(self):
        global _shared_state_manager
        if _shared_state_manager is None:
            _shared_state_manager = ConversationState(new_session=_shared_new_session)
        return _shared_state_manager

    @property
    def state_tool(self):
        return StateTool(self.state_manager)

    @property
    def solution_tool(self):
        return SolutionTool(self.state_manager)

    @property
    def documentation_tool(self):
        return DocumentationTool(self.state_manager)

    @classmethod
    def create(cls, new_session: bool = False):
        global _shared_new_session
        _shared_new_session = new_session
        return cls()

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended

    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def business_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['business_analyst'], # type: ignore[index]
            verbose=True,
            tools=[self.state_tool]
        )

    @agent
    def phase_coordinator(self) -> Agent:
        return Agent(
            config=self.agents_config['phase_coordinator'], # type: ignore[index]
            verbose=False,
            tools=[self.state_tool]
        )

    @agent
    def solution_designer(self) -> Agent:
        return Agent(
            config=self.agents_config['solution_designer'], # type: ignore[index]
            verbose=False,
            tools=[self.solution_tool]
        )

    @agent
    def solution_validator(self) -> Agent:
        return Agent(
            config=self.agents_config['solution_validator'], # type: ignore[index]
            verbose=False,
            tools=[self.solution_tool]
        )

    @agent
    def product_brief_writer(self) -> Agent:
        return Agent(
            config=self.agents_config['product_brief_writer'], # type: ignore[index]
            verbose=True,
            tools=[self.documentation_tool]
        )

    @agent
    def brief_reviewer(self) -> Agent:
        return Agent(
            config=self.agents_config['brief_reviewer'], # type: ignore[index]
            verbose=True,
            tools=[self.documentation_tool]
        )

    @agent
    def epic_story_writer(self) -> Agent:
        return Agent(
            config=self.agents_config['epic_story_writer'], # type: ignore[index]
            verbose=True,
            tools=[self.documentation_tool]
        )

    @agent
    def backlog_validator(self) -> Agent:
        return Agent(
            config=self.agents_config['backlog_validator'], # type: ignore[index]
            verbose=True,
            tools=[self.documentation_tool]
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['analysis_task'], # type: ignore[index]
        )

    @task
    def phase_evaluation_task(self) -> Task:
        return Task(
            config=self.tasks_config['phase_evaluation_task'], # type: ignore[index]
        )

    @task
    def solution_design_task(self) -> Task:
        return Task(
            config=self.tasks_config['solution_design_task'], # type: ignore[index]
        )

    @task
    def solution_validation_task(self) -> Task:
        return Task(
            config=self.tasks_config['solution_validation_task'], # type: ignore[index]
        )

    @task
    def solution_phase_evaluation_task(self) -> Task:
        return Task(
            config=self.tasks_config['solution_phase_evaluation_task'], # type: ignore[index]
        )

    @task
    def product_brief_creation_task(self) -> Task:
        return Task(
            config=self.tasks_config['product_brief_creation_task'], # type: ignore[index]
        )

    @task
    def product_brief_review_task(self) -> Task:
        return Task(
            config=self.tasks_config['product_brief_review_task'], # type: ignore[index]
        )

    @task
    def epic_story_creation_task(self) -> Task:
        return Task(
            config=self.tasks_config['epic_story_creation_task'], # type: ignore[index]
        )

    @task
    def backlog_validation_task(self) -> Task:
        return Task(
            config=self.tasks_config['backlog_validation_task'], # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Business Analyst crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=False,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )

    def run_analysis_conversation(self, user_message: str) -> tuple[str, bool, str]:
        """
        Run a single conversation turn in the analysis phase
        Returns: (ba_response, should_transition_to_solution, phase_evaluation)
        """
        # Save user message to state
        self.state_manager.add_message("user", user_message)

        # Get conversation context
        conversation_context = self.state_manager.get_conversation_summary()
        requirements_summary = self.state_manager.get_all_requirements_text()

        # Count turns BEFORE running agent
        turn_count = len([msg for msg in self.state_manager.state["conversation_history"] if msg["role"] == "user"])
        total_reqs = sum(len(v) for v in self.state_manager.get_requirements().values())

        # Create a crew with only analysis agents and tasks
        analysis_crew = Crew(
            agents=[self.business_analyst(), self.phase_coordinator()],
            tasks=[self.analysis_task(), self.phase_evaluation_task()],
            process=Process.sequential,
            verbose=False
        )

        # Run the crew with current context
        result = analysis_crew.kickoff(inputs={
            'user_message': user_message,
            'conversation_context': conversation_context,
            'requirements_summary': requirements_summary,
            'turn_count': turn_count,
            'total_requirements': total_reqs
        })

        # Extract BA response (from analysis_task)
        ba_response = str(result.tasks_output[0].raw)

        # Extract phase evaluation (from phase_evaluation_task)
        phase_evaluation = str(result.tasks_output[1].raw)

        # Save BA response to state
        self.state_manager.add_message("assistant", ba_response)

        # Check if we should transition to solution phase
        # Use actual state check instead of relying on agent's decision (which can hallucinate)
        is_complete, reason = self.state_manager.is_analysis_complete()

        # Count conversation turns (user messages only)
        turn_count = len([msg for msg in self.state_manager.state["conversation_history"] if msg["role"] == "user"])

        # Auto-transition if we have enough requirements
        total_reqs = sum(len(v) for v in self.state_manager.get_requirements().values())
        if total_reqs >= 6:
            is_complete = True
            reason = f"Đã thu thập {total_reqs} requirements - đủ để thiết kế giải pháp"

        should_transition = is_complete

        # If complete, modify BA response to inform user we're moving to next phase
        if should_transition:
            ba_response = ba_response + f"\n\n✅ Đã thu thập đủ thông tin! Chuyển sang giai đoạn thiết kế giải pháp..."

        return ba_response, should_transition, phase_evaluation

    def run_solution_phase(self) -> tuple[str, str, str, bool]:
        """
        Run the solution design phase
        Returns: (design_summary, validation_report, phase_evaluation, should_transition_to_documentation)
        """
        # Transition to solution phase
        self.state_manager.transition_to_phase("solution", "Analysis phase completed, moving to solution design")

        # Get requirements for solution design
        requirements_summary = self.state_manager.get_all_requirements_text()

        # Create a crew with solution agents and tasks
        solution_crew = Crew(
            agents=[self.solution_designer(), self.solution_validator(), self.phase_coordinator()],
            tasks=[self.solution_design_task(), self.solution_validation_task(), self.solution_phase_evaluation_task()],
            process=Process.sequential,
            verbose=False
        )

        # Get solution summary for validation
        solution_summary = self.state_manager.get_solution_text()

        # Run solution design crew
        result = solution_crew.kickoff(inputs={
            'requirements_summary': requirements_summary,
            'solution_summary': solution_summary,
            'validation_results': ""  # Will be filled by validation task
        })

        # Extract outputs
        design_summary = str(result.tasks_output[0].raw)
        validation_report = str(result.tasks_output[1].raw)
        phase_evaluation = str(result.tasks_output[2].raw)

        # Check if we should transition to documentation phase
        should_transition = "DECISION: READY" in phase_evaluation or "DECISION:READY" in phase_evaluation

        return design_summary, validation_report, phase_evaluation, should_transition

    def run_product_brief_phase(self, revision_feedback: str = "") -> tuple[str, bool, str]:
        """
        Run the Product Brief creation/revision phase
        Returns: (brief_text, needs_revision, review_comments)
        """
        # Transition to documentation phase if first time
        if self.state_manager.get_current_phase() != "documentation":
            self.state_manager.transition_to_phase("documentation", "Solution phase completed, moving to documentation")

        # Get requirements and solution for context
        requirements_summary = self.state_manager.get_all_requirements_text()
        solution_summary = self.state_manager.get_solution_text()

        # Create crew for Product Brief
        brief_crew = Crew(
            agents=[self.product_brief_writer(), self.brief_reviewer()],
            tasks=[self.product_brief_creation_task(), self.product_brief_review_task()],
            process=Process.sequential,
            verbose=True
        )

        # Run Product Brief crew
        result = brief_crew.kickoff(inputs={
            'requirements_summary': requirements_summary,
            'solution_summary': solution_summary,
            'revision_feedback': revision_feedback if revision_feedback else "None"
        })

        # Extract outputs
        creation_summary = str(result.tasks_output[0].raw)
        review_report = str(result.tasks_output[1].raw)

        # Get the created brief
        brief_text = self.state_manager.get_product_brief_text()

        # Check if revision is needed
        needs_revision = "REVIEW STATUS: NEEDS_REVISION" in review_report or "NEEDS_REVISION" in review_report

        return brief_text, needs_revision, review_report

    def run_backlog_phase(self, revision_feedback: str = "") -> tuple[str, bool, str]:
        """
        Run the Epics & Stories creation/revision phase
        Returns: (backlog_text, needs_revision, validation_report)
        """
        # Get solution for context
        solution_summary = self.state_manager.get_solution_text()

        # Create crew for Backlog
        backlog_crew = Crew(
            agents=[self.epic_story_writer(), self.backlog_validator()],
            tasks=[self.epic_story_creation_task(), self.backlog_validation_task()],
            process=Process.sequential,
            verbose=True
        )

        # Run Backlog crew
        result = backlog_crew.kickoff(inputs={
            'solution_summary': solution_summary,
            'revision_feedback': revision_feedback if revision_feedback else "None"
        })

        # Extract outputs
        creation_summary = str(result.tasks_output[0].raw)
        validation_report = str(result.tasks_output[1].raw)

        # Get the created backlog
        backlog_text = self.state_manager.get_backlog_text()

        # Check if revision is needed
        needs_revision = "VALIDATION STATUS: INCOMPLETE" in validation_report or "INCOMPLETE" in validation_report

        return backlog_text, needs_revision, validation_report
