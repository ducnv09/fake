"""
Flow State Model for Business Analyst Flow
Replaces manual JSON state management with Pydantic-based state
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime


class BAFlowState(BaseModel):
    """
    Structured state for the Business Analyst Flow
    Automatically managed by CrewAI Flow
    """

    # ==================== ANALYSIS PHASE ====================
    requirements: Dict[str, List[str]] = Field(
        default_factory=lambda: {
            "problem_goals": [],
            "users_stakeholders": [],
            "features_scope": []
        },
        description="Requirements collected during analysis phase"
    )

    conversation_history: List[Dict[str, str]] = Field(
        default_factory=list,
        description="History of user-assistant conversations"
    )

    current_phase: str = Field(
        default="analysis",
        description="Current workflow phase: analysis, solution, or documentation"
    )

    # ==================== SOLUTION PHASE ====================
    solution: Dict[str, List[Dict]] = Field(
        default_factory=lambda: {
            "business_flows": []     # User journeys and workflows
        },
        description="Solution components designed during solution phase - focused on business flows only"
    )

    # ==================== USER INTERACTION ====================
    user_choices: List[Dict] = Field(
        default_factory=list,
        description="History of user choices made through interactive questions"
    )

    pending_user_question: Optional[Dict] = Field(
        default=None,
        description="Current question waiting for user response"
    )

    # ==================== PHASE APPROVALS & REFINEMENTS ====================
    phase_approvals: Dict[str, List[Dict]] = Field(
        default_factory=lambda: {
            "solution_approved": [],
            "brief_approved": [],
            "backlog_approved": []
        },
        description="Track user approvals/rejections and refinement requests for each phase"
    )

    refinement_history: List[Dict] = Field(
        default_factory=list,
        description="History of refinements/changes requested by user"
    )

    # ==================== DOCUMENTATION PHASE ====================
    documentation: Dict = Field(
        default_factory=lambda: {
            "product_brief": {
                "product_summary": "",
                "problem_statement": "",
                "target_users": "",
                "product_goals": "",
                "scope": "",
                "revision_count": 0
            },
            "epics": [],
            "stories": []
        },
        description="Documentation created during documentation phase"
    )

    # ==================== METADATA ====================
    session_id: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S"),
        description="Unique session identifier"
    )

    started_at: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Timestamp when flow started"
    )

    phase_transitions: List[Dict[str, str]] = Field(
        default_factory=list,
        description="History of phase transitions"
    )

    # ==================== HELPER PROPERTIES ====================

    def add_message(self, role: str, content: str):
        """Add a message to conversation history"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.conversation_history.append(message)

    def add_requirement(self, category: str, requirement: str) -> bool:
        """Add a requirement to a specific category"""
        if category in self.requirements:
            if requirement not in self.requirements[category]:
                self.requirements[category].append(requirement)
                return True
        return False

    def transition_to_phase(self, new_phase: str, reason: str = ""):
        """Transition to a new phase"""
        old_phase = self.current_phase
        self.current_phase = new_phase

        transition = {
            "from": old_phase,
            "to": new_phase,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
        self.phase_transitions.append(transition)

    def is_analysis_complete(self) -> tuple[bool, str]:
        """
        Check if analysis phase has enough information
        Returns: (is_complete, reason)
        """
        problem_count = len(self.requirements["problem_goals"])
        users_count = len(self.requirements["users_stakeholders"])
        features_count = len(self.requirements["features_scope"])
        total_count = problem_count + users_count + features_count

        # Flexible criteria
        if problem_count >= 1 and users_count >= 1 and features_count >= 1 and total_count >= 5:
            return True, f"Sufficient requirements: {problem_count} goals, {users_count} stakeholders, {features_count} features"

        if problem_count >= 2 and users_count >= 2 and features_count >= 2:
            return True, f"Sufficient requirements: {problem_count} goals, {users_count} stakeholders, {features_count} features"

        if total_count >= 8:
            return True, f"Total of {total_count} requirements collected"

        missing = []
        if problem_count < 2:
            missing.append(f"problem/goals ({problem_count}/2)")
        if users_count < 2:
            missing.append(f"users/stakeholders ({users_count}/2)")
        if features_count < 2:
            missing.append(f"features/scope ({features_count}/2)")

        return False, f"Need more: {', '.join(missing)}"

    def get_all_requirements_text(self) -> str:
        """Get all requirements as formatted text"""
        text = []

        if self.requirements["problem_goals"]:
            text.append("## Problem & Goals")
            for i, req in enumerate(self.requirements["problem_goals"], 1):
                text.append(f"{i}. {req}")
            text.append("")

        if self.requirements["users_stakeholders"]:
            text.append("## Users & Stakeholders")
            for i, req in enumerate(self.requirements["users_stakeholders"], 1):
                text.append(f"{i}. {req}")
            text.append("")

        if self.requirements["features_scope"]:
            text.append("## Features & Scope")
            for i, req in enumerate(self.requirements["features_scope"], 1):
                text.append(f"{i}. {req}")
            text.append("")

        return "\n".join(text)

    def get_solution_text(self) -> str:
        """Get all solution components as formatted text"""
        text = []

        # Business Flows
        if self.solution["business_flows"]:
            text.append("## Business Flows")
            for i, flow in enumerate(self.solution["business_flows"], 1):
                text.append(f"\n### {i}. {flow.get('name', 'Unnamed Flow')}")
                if flow.get('description'):
                    text.append(f"**Description:** {flow['description']}")
                if flow.get('steps'):
                    text.append("**Steps:**")
                    for j, step in enumerate(flow['steps'], 1):
                        text.append(f"  {j}. {step}")
                if flow.get('actors'):
                    text.append(f"**Actors:** {', '.join(flow['actors'])}")
            text.append("")

        return "\n".join(text) if text else "No solution components defined yet."

    def get_product_brief_text(self) -> str:
        """Get Product Brief as formatted text"""
        print(f"\n[STATE DEBUG] get_product_brief_text called")
        print(f"[STATE DEBUG] documentation dict: {self.documentation}")
        brief = self.documentation["product_brief"]
        print(f"[STATE DEBUG] brief: {brief}")
        print(f"[STATE DEBUG] brief.get('product_summary'): {brief.get('product_summary') if brief else 'brief is None'}")
        if not brief or not brief.get("product_summary"):
            return "No Product Brief created yet."

        text = []
        text.append("# PRODUCT BRIEF\n")

        if brief.get("product_summary"):
            text.append("## Product Summary")
            text.append(brief["product_summary"])
            text.append("")

        if brief.get("problem_statement"):
            text.append("## Problem Statement")
            text.append(brief["problem_statement"])
            text.append("")

        if brief.get("target_users"):
            text.append("## Target Users")
            text.append(brief["target_users"])
            text.append("")

        if brief.get("product_goals"):
            text.append("## Product Goals")
            text.append(brief["product_goals"])
            text.append("")

        if brief.get("scope"):
            text.append("## Scope")
            text.append(brief["scope"])
            text.append("")

        return "\n".join(text)

    def get_backlog_text(self) -> str:
        """Get Epics and Stories as formatted text"""
        epics = self.documentation["epics"]
        stories = self.documentation["stories"]

        if not epics and not stories:
            return "No Epics or Stories created yet."

        text = []
        text.append("# PRODUCT BACKLOG\n")

        if epics:
            text.append("## Epics\n")
            for i, epic in enumerate(epics, 1):
                text.append(f"### Epic {i}: {epic.get('name', 'Unnamed Epic')}")
                text.append(f"**Domain:** {epic.get('domain', 'N/A')}")
                text.append(f"**Description:** {epic.get('description', 'N/A')}")

                # Find stories for this epic
                epic_stories = [s for s in stories if s.get('epic_id') == epic.get('id')]
                if epic_stories:
                    text.append(f"\n**User Stories ({len(epic_stories)}):**")
                    for j, story in enumerate(epic_stories, 1):
                        text.append(f"\n{i}.{j}. {story.get('title', 'Untitled Story')}")
                        text.append(f"   **Description:** {story.get('description', 'N/A')}")
                        if story.get('acceptance_criteria'):
                            text.append(f"   **Acceptance Criteria:**")
                            for criterion in story['acceptance_criteria']:
                                text.append(f"   - {criterion}")
                text.append("")

        return "\n".join(text)

    # ==================== NEW HELPER METHODS ====================

    def add_user_choice(self, context: str, question: str, selected_label: str, selected_value: str) -> bool:
        """Record a user choice from interactive question"""
        choice = {
            "context": context,
            "question": question,
            "selected_label": selected_label,
            "selected_value": selected_value,
            "timestamp": datetime.now().isoformat()
        }
        self.user_choices.append(choice)

        # Clear pending question
        self.pending_user_question = None
        return True

    def request_approval(self, phase: str, content: Dict, approval_type: str = "preview") -> bool:
        """Request user approval for phase output"""
        if phase not in self.phase_approvals:
            self.phase_approvals[phase] = []

        approval_request = {
            "type": approval_type,
            "content": content,
            "status": "pending",
            "timestamp": datetime.now().isoformat()
        }
        self.phase_approvals[phase].append(approval_request)
        return True

    def record_approval(self, phase: str, approved: bool, feedback: str = "") -> bool:
        """Record user approval/rejection"""
        if phase not in self.phase_approvals or not self.phase_approvals[phase]:
            return False

        # Update the most recent pending approval
        for approval in reversed(self.phase_approvals[phase]):
            if approval.get("status") == "pending":
                approval["status"] = "approved" if approved else "rejected"
                approval["feedback"] = feedback
                approval["resolved_at"] = datetime.now().isoformat()

                # Record refinement if rejected
                if not approved and feedback:
                    self.add_refinement(phase, feedback)

                return True

        return False

    def add_refinement(self, phase: str, request: str) -> bool:
        """Add a refinement request"""
        refinement = {
            "phase": phase,
            "request": request,
            "timestamp": datetime.now().isoformat()
        }
        self.refinement_history.append(refinement)
        return True

    def validate_product_brief(self) -> tuple[bool, List[str]]:
        """
        Validate Product Brief for missing fields
        Returns: (is_complete, list_of_missing_fields)
        """
        brief = self.documentation["product_brief"]
        required_fields = [
            "product_summary",
            "problem_statement",
            "target_users",
            "product_goals",
            "scope"
        ]

        missing_fields = []
        for field in required_fields:
            value = brief.get(field, "").strip()
            if not value or value == "":
                missing_fields.append(field)

        is_complete = len(missing_fields) == 0
        return is_complete, missing_fields

    def get_brief_missing_info(self) -> str:
        """Get formatted text about missing Product Brief information"""
        is_complete, missing = self.validate_product_brief()

        if is_complete:
            return "✅ Product Brief is complete. All required fields are filled."

        text = ["⚠️ Product Brief is INCOMPLETE. Missing fields:"]
        for field in missing:
            # Convert field name to readable format
            readable = field.replace("_", " ").title()
            text.append(f"  - {readable}")

        text.append("\nPlease gather this information from the user or requirements.")
        return "\n".join(text)

    def get_progress_summary(self) -> Dict[str, any]:
        """Get progress summary for all phases"""
        return {
            "current_phase": self.current_phase,
            "analysis": {
                "complete": self.is_analysis_complete()[0],
                "requirements_count": sum(len(reqs) for reqs in self.requirements.values())
            },
            "solution": {
                "components_count": sum(len(comps) for comps in self.solution.values())
            },
            "documentation": {
                "brief_created": bool(self.documentation["product_brief"].get("product_summary")),
                "brief_complete": self.validate_product_brief()[0],
                "epics_count": len(self.documentation["epics"]),
                "stories_count": len(self.documentation["stories"])
            },
            "user_interactions": {
                "choices_made": len(self.user_choices),
                "pending_question": bool(self.pending_user_question)
            }
        }
