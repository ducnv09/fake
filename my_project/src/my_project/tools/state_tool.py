"""
Custom tool for agents to interact with Flow state
Updated to work with CrewAI Flow instead of manual ConversationState
"""

from crewai.tools import BaseTool
from typing import Type, Optional, Any
from pydantic import BaseModel, Field


class StateToolInput(BaseModel):
    """Input schema for FlowStateTool"""
    action: str = Field(..., description="Action to perform: 'add_requirement', 'add_requirements_batch', 'get_requirements', 'get_summary', 'check_complete'")
    category: Optional[str] = Field(None, description="Category: 'problem_goals', 'users_stakeholders', or 'features_scope'")
    content: Optional[str] = Field(None, description="Content to add (for add_requirement action)")
    requirements: Optional[list] = Field(None, description="List of {category, content} dicts for batch add")


class FlowStateTool(BaseTool):
    name: str = "State Manager Tool"
    description: str = """
    Tool to interact with Flow state. Use this to:
    - Add single requirement: action='add_requirement', category='problem_goals|users_stakeholders|features_scope', content='requirement text'
    - Add multiple requirements at once (RECOMMENDED): action='add_requirements_batch', requirements=[{'category': 'problem_goals', 'content': 'req1'}, {'category': 'users_stakeholders', 'content': 'req2'}, ...]
    - Get requirements: action='get_requirements', category='problem_goals|users_stakeholders|features_scope' (or omit category for all)
    - Get summary: action='get_summary'
    - Check if analysis complete: action='check_complete'
    """
    args_schema: Type[BaseModel] = StateToolInput
    flow: Any = Field(default=None, exclude=True)

    def __init__(self, flow: Any, **kwargs):
        super().__init__(**kwargs)
        object.__setattr__(self, 'flow', flow)

    def _run(self, action: str, category: Optional[str] = None, content: Optional[str] = None, requirements: Optional[list] = None) -> str:
        """Execute the tool action"""

        if action == "add_requirement":
            if not category or not content:
                return "Error: 'add_requirement' requires both 'category' and 'content'"

            print(f"\n[TOOL DEBUG] Before add: {self.flow.state.requirements}")
            success = self.flow.state.add_requirement(category, content)
            print(f"[TOOL DEBUG] After add: {self.flow.state.requirements}")
            print(f"[TOOL DEBUG] Success: {success}")

            if success:
                return f"Successfully added requirement to {category}: {content}"
            else:
                return f"Failed to add requirement. Invalid category: {category}"

        elif action == "add_requirements_batch":
            if not requirements or not isinstance(requirements, list):
                return "Error: 'add_requirements_batch' requires 'requirements' as a list of {category, content} dicts"

            print(f"\n[TOOL DEBUG BATCH] Before batch add: {self.flow.state.requirements}")
            added_count = 0
            failed = []

            for req in requirements:
                if not isinstance(req, dict) or 'category' not in req or 'content' not in req:
                    failed.append(f"Invalid requirement format: {req}")
                    continue

                success = self.flow.state.add_requirement(req['category'], req['content'])
                if success:
                    added_count += 1
                else:
                    failed.append(f"Failed to add: {req}")

            print(f"[TOOL DEBUG BATCH] After batch add: {self.flow.state.requirements}")
            print(f"[TOOL DEBUG BATCH] Added: {added_count}, Failed: {len(failed)}")

            result = f"Batch add completed: {added_count} requirements added successfully"
            if failed:
                result += f"\n{len(failed)} failed:\n" + "\n".join(failed)
            return result

        elif action == "get_requirements":
            if category:
                reqs = self.flow.state.requirements.get(category, [])
                if not reqs:
                    return f"No requirements found in category: {category}"
                return f"Requirements in {category}:\n" + "\n".join(f"- {r}" for r in reqs)
            else:
                # Return all requirements
                return self.flow.state.get_all_requirements_text()

        elif action == "get_summary":
            return self.flow._get_conversation_summary()

        elif action == "check_complete":
            is_complete, reason = self.flow.state.is_analysis_complete()
            status = "COMPLETE" if is_complete else "INCOMPLETE"
            return f"Analysis Status: {status}\nReason: {reason}"

        else:
            return f"Error: Unknown action '{action}'. Valid actions: add_requirement, get_requirements, get_summary, check_complete"


# ==================== LEGACY: For backward compatibility with old crew.py ====================

class StateTool(BaseTool):
    """
    Legacy StateTool for backward compatibility with old crew.py
    Works with ConversationState (manual JSON state)
    """
    name: str = "State Manager Tool"
    description: str = """
    Tool to interact with conversation state. Use this to:
    - Add requirements: action='add_requirement', category='problem_goals|users_stakeholders|features_scope', content='requirement text'
    - Get requirements: action='get_requirements', category='problem_goals|users_stakeholders|features_scope' (or omit category for all)
    - Get summary: action='get_summary'
    - Check if analysis complete: action='check_complete'
    """
    args_schema: Type[BaseModel] = StateToolInput
    state_manager: Any = Field(default=None, exclude=True)

    def __init__(self, state_manager: Any, **kwargs):
        super().__init__(**kwargs)
        object.__setattr__(self, 'state_manager', state_manager)

    def _run(self, action: str, category: Optional[str] = None, content: Optional[str] = None) -> str:
        """Execute the tool action"""

        if action == "add_requirement":
            if not category or not content:
                return "Error: 'add_requirement' requires both 'category' and 'content'"

            success = self.state_manager.add_requirement(category, content)
            if success:
                return f"Successfully added requirement to {category}: {content}"
            else:
                return f"Failed to add requirement. Invalid category: {category}"

        elif action == "get_requirements":
            reqs = self.state_manager.get_requirements(category)
            if category:
                if not reqs:
                    return f"No requirements found in category: {category}"
                return f"Requirements in {category}:\n" + "\n".join(f"- {r}" for r in reqs)
            else:
                # Return all requirements
                return self.state_manager.get_all_requirements_text()

        elif action == "get_summary":
            return self.state_manager.get_conversation_summary()

        elif action == "check_complete":
            is_complete, reason = self.state_manager.is_analysis_complete()
            status = "COMPLETE" if is_complete else "INCOMPLETE"
            return f"Analysis Status: {status}\nReason: {reason}"

        else:
            return f"Error: Unknown action '{action}'. Valid actions: add_requirement, get_requirements, get_summary, check_complete"


class RequirementExtractorInput(BaseModel):
    """Input schema for RequirementExtractor"""
    user_message: str = Field(..., description="The user's message to analyze")


class RequirementExtractorTool(BaseTool):
    name: str = "Requirement Extractor"
    description: str = """
    Analyzes user messages and extracts structured requirements.
    Use this to parse what the user said and identify:
    - Problems and goals they want to solve
    - Users and stakeholders involved
    - Features and scope they mentioned
    Returns structured information to save to state.
    """
    args_schema: Type[BaseModel] = RequirementExtractorInput

    def _run(self, user_message: str) -> str:
        """
        This is a simple keyword-based extractor.
        In production, you might use an LLM call here for better extraction.
        """
        message_lower = user_message.lower()

        findings = {
            "problem_goals": [],
            "users_stakeholders": [],
            "features_scope": []
        }

        # Simple keyword detection
        problem_keywords = ["problem", "issue", "challenge", "goal", "objective", "need", "want", "solve"]
        user_keywords = ["user", "customer", "admin", "stakeholder", "client", "manager", "team"]
        feature_keywords = ["feature", "function", "capability", "should", "must", "requirement", "need to"]

        # Check for problem/goal indicators
        if any(keyword in message_lower for keyword in problem_keywords):
            findings["problem_goals"].append(f"User mentioned: {user_message[:100]}")

        # Check for user/stakeholder mentions
        if any(keyword in message_lower for keyword in user_keywords):
            findings["users_stakeholders"].append(f"Stakeholder info: {user_message[:100]}")

        # Check for feature mentions
        if any(keyword in message_lower for keyword in feature_keywords):
            findings["features_scope"].append(f"Feature requirement: {user_message[:100]}")

        # Format output
        result = "Extracted information:\n"
        for category, items in findings.items():
            if items:
                result += f"\n{category}:\n"
                for item in items:
                    result += f"  - {item}\n"

        if not any(findings.values()):
            result += "\nNo specific requirements detected. Consider asking follow-up questions."

        return result
