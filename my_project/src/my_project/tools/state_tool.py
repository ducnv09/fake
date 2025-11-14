"""
Custom tool for agents to interact with conversation state
"""

from crewai.tools import BaseTool
from typing import Type, Optional
from pydantic import BaseModel, Field
import sys
from pathlib import Path

# Add parent directory to path to import state_manager
sys.path.insert(0, str(Path(__file__).parent.parent))
from state_manager import ConversationState


class StateToolInput(BaseModel):
    """Input schema for StateTool"""
    action: str = Field(..., description="Action to perform: 'add_requirement', 'get_requirements', 'get_summary', 'check_complete'")
    category: Optional[str] = Field(None, description="Category: 'problem_goals', 'users_stakeholders', or 'features_scope'")
    content: Optional[str] = Field(None, description="Content to add (for add_requirement action)")


class StateTool(BaseTool):
    name: str = "State Manager Tool"
    description: str = """
    Tool to interact with conversation state. Use this to:
    - Add requirements: action='add_requirement', category='problem_goals|users_stakeholders|features_scope', content='requirement text'
    - Get requirements: action='get_requirements', category='problem_goals|users_stakeholders|features_scope' (or omit category for all)
    - Get summary: action='get_summary'
    - Check if analysis complete: action='check_complete'
    """
    args_schema: Type[BaseModel] = StateToolInput
    state_manager: ConversationState = Field(default=None, exclude=True)

    def __init__(self, state_manager: ConversationState, **kwargs):
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
