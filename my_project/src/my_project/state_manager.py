"""
State Manager for Business Analyst Conversation System
Handles conversation state persistence and requirement tracking
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path


class ConversationState:
    """Manages the conversation state for the BA system"""

    PHASES = ["analysis", "solution", "documentation"]

    def __init__(self, state_file: str = "conversation_state.json", new_session: bool = False):
        self.state_file = state_file
        if new_session:
            # Force create new session
            self.state = self._create_initial_state()
            self.save()
        else:
            self.state = self._load_or_initialize()

    def _load_or_initialize(self) -> Dict:
        """Load existing state or create new one"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Could not parse {self.state_file}, creating new state")
                return self._create_initial_state()
        else:
            return self._create_initial_state()

    def _create_initial_state(self) -> Dict:
        """Create initial conversation state"""
        return {
            "current_phase": "analysis",
            "requirements": {
                "problem_goals": [],
                "users_stakeholders": [],
                "features_scope": []
            },
            "solution": {
                "frontend_components": [],
                "backend_components": [],
                "business_flows": []
            },
            "documentation": {
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
            "conversation_history": [],
            "metadata": {
                "session_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "started_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            },
            "phase_transitions": []
        }

    def save(self):
        """Save current state to file"""
        self.state["metadata"]["updated_at"] = datetime.now().isoformat()
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    def add_message(self, role: str, content: str):
        """Add a message to conversation history"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.state["conversation_history"].append(message)
        self.save()

    def add_requirement(self, category: str, requirement: str):
        """Add a requirement to a specific category"""
        if category in self.state["requirements"]:
            if requirement not in self.state["requirements"][category]:
                self.state["requirements"][category].append(requirement)
                self.save()
                return True
        return False

    def get_requirements(self, category: Optional[str] = None) -> Dict or List:
        """Get requirements by category or all requirements"""
        if category:
            return self.state["requirements"].get(category, [])
        return self.state["requirements"]

    def get_current_phase(self) -> str:
        """Get current phase"""
        return self.state["current_phase"]

    def transition_to_phase(self, new_phase: str, reason: str = ""):
        """Transition to a new phase"""
        if new_phase in self.PHASES:
            old_phase = self.state["current_phase"]
            self.state["current_phase"] = new_phase

            transition = {
                "from": old_phase,
                "to": new_phase,
                "reason": reason,
                "timestamp": datetime.now().isoformat()
            }
            self.state["phase_transitions"].append(transition)
            self.save()
            return True
        return False

    def is_analysis_complete(self) -> tuple[bool, str]:
        """
        Check if analysis phase has enough information
        Returns: (is_complete, reason)
        """
        reqs = self.state["requirements"]

        # Check if we have at least some requirements in each category
        problem_count = len(reqs["problem_goals"])
        users_count = len(reqs["users_stakeholders"])
        features_count = len(reqs["features_scope"])

        total_count = problem_count + users_count + features_count

        # More flexible criteria: at least 1 in each category AND 5+ total, OR 8+ total
        if problem_count >= 1 and users_count >= 1 and features_count >= 1 and total_count >= 5:
            return True, f"Sufficient requirements collected: {problem_count} goals, {users_count} stakeholders, {features_count} features"

        if problem_count >= 2 and users_count >= 2 and features_count >= 2:
            return True, f"Sufficient requirements collected: {problem_count} goals, {users_count} stakeholders, {features_count} features"

        if total_count >= 8:
            return True, f"Total of {total_count} requirements collected across categories"

        missing = []
        if problem_count < 2:
            missing.append(f"problem/goals ({problem_count}/2)")
        if users_count < 2:
            missing.append(f"users/stakeholders ({users_count}/2)")
        if features_count < 2:
            missing.append(f"features/scope ({features_count}/2)")

        return False, f"Need more information in: {', '.join(missing)}"

    def get_conversation_summary(self) -> str:
        """Get a summary of the conversation for context"""
        reqs = self.state["requirements"]
        history_count = len(self.state["conversation_history"])

        summary = f"""
Current Phase: {self.state["current_phase"]}
Conversation Messages: {history_count}

Requirements Collected:
- Problem & Goals: {len(reqs["problem_goals"])} items
- Users & Stakeholders: {len(reqs["users_stakeholders"])} items
- Features & Scope: {len(reqs["features_scope"])} items

Total Requirements: {sum(len(v) for v in reqs.values())}
"""
        return summary.strip()

    def get_all_requirements_text(self) -> str:
        """Get all requirements as formatted text"""
        reqs = self.state["requirements"]
        text = []

        if reqs["problem_goals"]:
            text.append("## Problem & Goals")
            for i, req in enumerate(reqs["problem_goals"], 1):
                text.append(f"{i}. {req}")
            text.append("")

        if reqs["users_stakeholders"]:
            text.append("## Users & Stakeholders")
            for i, req in enumerate(reqs["users_stakeholders"], 1):
                text.append(f"{i}. {req}")
            text.append("")

        if reqs["features_scope"]:
            text.append("## Features & Scope")
            for i, req in enumerate(reqs["features_scope"], 1):
                text.append(f"{i}. {req}")
            text.append("")

        return "\n".join(text)

    # ==================== SOLUTION PHASE METHODS ====================

    def add_frontend_component(self, component: Dict) -> bool:
        """Add a frontend component to solution"""
        if "solution" not in self.state:
            self.state["solution"] = {"frontend_components": [], "backend_components": [], "business_flows": []}

        self.state["solution"]["frontend_components"].append(component)
        self.save()
        return True

    def add_backend_component(self, component: Dict) -> bool:
        """Add a backend component to solution"""
        if "solution" not in self.state:
            self.state["solution"] = {"frontend_components": [], "backend_components": [], "business_flows": []}

        self.state["solution"]["backend_components"].append(component)
        self.save()
        return True

    def add_business_flow(self, flow: Dict) -> bool:
        """Add a business flow to solution"""
        if "solution" not in self.state:
            self.state["solution"] = {"frontend_components": [], "backend_components": [], "business_flows": []}

        self.state["solution"]["business_flows"].append(flow)
        self.save()
        return True

    def get_solution(self) -> Dict:
        """Get all solution components"""
        if "solution" not in self.state:
            return {"frontend_components": [], "backend_components": [], "business_flows": []}
        return self.state["solution"]

    def get_solution_summary(self) -> str:
        """Get a summary of the solution"""
        solution = self.get_solution()

        frontend_count = len(solution.get("frontend_components", []))
        backend_count = len(solution.get("backend_components", []))
        flows_count = len(solution.get("business_flows", []))

        summary = f"""
Solution Components:
- Frontend Components: {frontend_count} items
- Backend Components: {backend_count} items
- Business Flows: {flows_count} items

Total Solution Elements: {frontend_count + backend_count + flows_count}
"""
        return summary.strip()

    def get_solution_text(self) -> str:
        """Get all solution components as formatted text"""
        solution = self.get_solution()
        text = []

        # Frontend Components
        if solution.get("frontend_components"):
            text.append("## Frontend Components")
            for i, comp in enumerate(solution["frontend_components"], 1):
                text.append(f"\n### {i}. {comp.get('name', 'Unnamed Component')}")
                if comp.get('description'):
                    text.append(f"**Description:** {comp['description']}")
                if comp.get('features'):
                    text.append(f"**Features:** {', '.join(comp['features'])}")
                if comp.get('user_interactions'):
                    text.append(f"**User Interactions:** {', '.join(comp['user_interactions'])}")
            text.append("")

        # Backend Components
        if solution.get("backend_components"):
            text.append("## Backend Components")
            for i, comp in enumerate(solution["backend_components"], 1):
                text.append(f"\n### {i}. {comp.get('name', 'Unnamed Component')}")
                if comp.get('description'):
                    text.append(f"**Description:** {comp['description']}")
                if comp.get('endpoints'):
                    text.append(f"**Endpoints:** {', '.join(comp['endpoints'])}")
                if comp.get('business_logic'):
                    text.append(f"**Business Logic:** {', '.join(comp['business_logic'])}")
                if comp.get('data_models'):
                    text.append(f"**Data Models:** {', '.join(comp['data_models'])}")
            text.append("")

        # Business Flows
        if solution.get("business_flows"):
            text.append("## Business Flows")
            for i, flow in enumerate(solution["business_flows"], 1):
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

    def is_solution_complete(self) -> tuple[bool, str]:
        """
        Check if solution phase has enough components
        Returns: (is_complete, reason)
        """
        solution = self.get_solution()

        frontend_count = len(solution.get("frontend_components", []))
        backend_count = len(solution.get("backend_components", []))
        flows_count = len(solution.get("business_flows", []))

        total_count = frontend_count + backend_count + flows_count

        # Need at least 2 components in each category or 6 total
        if frontend_count >= 2 and backend_count >= 2 and flows_count >= 1:
            return True, f"Sufficient solution components: {frontend_count} frontend, {backend_count} backend, {flows_count} flows"

        if total_count >= 6:
            return True, f"Total of {total_count} solution components defined"

        missing = []
        if frontend_count < 2:
            missing.append(f"frontend components ({frontend_count}/2)")
        if backend_count < 2:
            missing.append(f"backend components ({backend_count}/2)")
        if flows_count < 1:
            missing.append(f"business flows ({flows_count}/1)")

        return False, f"Need more solution components in: {', '.join(missing)}"

    # ==================== DOCUMENTATION PHASE METHODS ====================

    def save_product_brief(self, brief_data: Dict) -> bool:
        """Save Product Brief"""
        if "documentation" not in self.state:
            self.state["documentation"] = {"product_brief": {}, "epics": [], "stories": []}

        self.state["documentation"]["product_brief"] = {
            "product_summary": brief_data.get("product_summary", ""),
            "problem_statement": brief_data.get("problem_statement", ""),
            "target_users": brief_data.get("target_users", ""),
            "product_goals": brief_data.get("product_goals", ""),
            "scope": brief_data.get("scope", ""),
            "revision_count": brief_data.get("revision_count", 0)
        }
        self.save()
        return True

    def get_product_brief(self) -> Dict:
        """Get Product Brief"""
        if "documentation" not in self.state:
            return {}
        return self.state["documentation"].get("product_brief", {})

    def add_epic(self, epic_data: Dict) -> bool:
        """Add an Epic"""
        if "documentation" not in self.state:
            self.state["documentation"] = {"product_brief": {}, "epics": [], "stories": []}

        self.state["documentation"]["epics"].append(epic_data)
        self.save()
        return True

    def add_story(self, story_data: Dict) -> bool:
        """Add a User Story"""
        if "documentation" not in self.state:
            self.state["documentation"] = {"product_brief": {}, "epics": [], "stories": []}

        self.state["documentation"]["stories"].append(story_data)
        self.save()
        return True

    def get_epics(self) -> List[Dict]:
        """Get all Epics"""
        if "documentation" not in self.state:
            return []
        return self.state["documentation"].get("epics", [])

    def get_stories(self) -> List[Dict]:
        """Get all User Stories"""
        if "documentation" not in self.state:
            return []
        return self.state["documentation"].get("stories", [])

    def get_product_brief_text(self) -> str:
        """Get Product Brief as formatted text"""
        brief = self.get_product_brief()
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
        epics = self.get_epics()
        stories = self.get_stories()

        if not epics and not stories:
            return "No Epics or Stories created yet."

        text = []
        text.append("# PRODUCT BACKLOG\n")

        # Group stories by epic
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

    def get_documentation_text(self) -> str:
        """Get complete documentation (Brief + Backlog)"""
        brief_text = self.get_product_brief_text()
        backlog_text = self.get_backlog_text()

        return f"{brief_text}\n\n{'='*70}\n\n{backlog_text}"

    def reset(self):
        """Reset to initial state"""
        self.state = self._create_initial_state()
        self.save()
