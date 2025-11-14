"""
Custom tool for agents to interact with documentation (Product Brief, Epics, Stories)
"""

from crewai.tools import BaseTool
from typing import Type, Optional, Dict, Any
from pydantic import BaseModel, Field
import sys
import json
from pathlib import Path

# Add parent directory to path to import state_manager
sys.path.insert(0, str(Path(__file__).parent.parent))
from state_manager import ConversationState


class DocumentationToolInput(BaseModel):
    """Input schema for DocumentationTool"""
    action: str = Field(..., description="Action to perform: 'save_brief', 'get_brief', 'add_epic', 'add_story', 'get_documentation'")
    data: Optional[str] = Field(None, description="JSON string of data (for save/add actions)")


class DocumentationTool(BaseTool):
    name: str = "Documentation Manager Tool"
    description: str = """
    Tool to manage documentation (Product Brief, Epics, Stories). Use this to:
    - Save Product Brief: action='save_brief', data='{"product_summary": "...", "problem_statement": "...", "target_users": "...", "product_goals": "...", "scope": "...", "revision_count": 0}'
    - Get Product Brief: action='get_brief'
    - Add Epic: action='add_epic', data='{"id": "epic-1", "name": "...", "description": "...", "domain": "..."}'
    - Add Story: action='add_story', data='{"epic_id": "epic-1", "title": "...", "description": "...", "acceptance_criteria": [...]}'
    - Get documentation: action='get_documentation'
    """
    args_schema: Type[BaseModel] = DocumentationToolInput
    state_manager: ConversationState = Field(default=None, exclude=True)

    def __init__(self, state_manager: ConversationState, **kwargs):
        super().__init__(**kwargs)
        object.__setattr__(self, 'state_manager', state_manager)

    def _run(self, action: str, data: Optional[str] = None) -> str:
        """Execute the tool action"""

        if action == "save_brief":
            if not data:
                return "Error: 'save_brief' requires 'data'"

            try:
                brief_data = json.loads(data)
                success = self.state_manager.save_product_brief(brief_data)
                if success:
                    return "Successfully saved Product Brief"
                else:
                    return "Failed to save Product Brief"
            except json.JSONDecodeError as e:
                return f"Error: Invalid JSON in data: {e}"

        elif action == "get_brief":
            brief = self.state_manager.get_product_brief()
            if brief:
                return json.dumps(brief, indent=2)
            else:
                return "No Product Brief found"

        elif action == "add_epic":
            if not data:
                return "Error: 'add_epic' requires 'data'"

            try:
                epic_data = json.loads(data)
                success = self.state_manager.add_epic(epic_data)
                if success:
                    return f"Successfully added Epic: {epic_data.get('name', 'Unnamed')}"
                else:
                    return "Failed to add Epic"
            except json.JSONDecodeError as e:
                return f"Error: Invalid JSON in data: {e}"

        elif action == "add_story":
            if not data:
                return "Error: 'add_story' requires 'data'"

            try:
                story_data = json.loads(data)
                success = self.state_manager.add_story(story_data)
                if success:
                    return f"Successfully added Story: {story_data.get('title', 'Untitled')}"
                else:
                    return "Failed to add Story"
            except json.JSONDecodeError as e:
                return f"Error: Invalid JSON in data: {e}"

        elif action == "get_documentation":
            return self.state_manager.get_documentation_text()

        else:
            return f"Error: Unknown action '{action}'. Valid actions: save_brief, get_brief, add_epic, add_story, get_documentation"
