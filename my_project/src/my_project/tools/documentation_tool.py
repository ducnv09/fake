"""
Custom tool for agents to interact with documentation (Product Brief, Epics, Stories)
Updated to work with CrewAI Flow instead of manual ConversationState
"""

from crewai.tools import BaseTool
from typing import Type, Optional, Any
from pydantic import BaseModel, Field
import json


class DocumentationToolInput(BaseModel):
    """Input schema for FlowDocumentationTool"""
    action: str = Field(..., description="Action to perform: 'save_brief', 'get_brief', 'validate_brief', 'add_epic', 'add_story', 'get_documentation', 'validate_epic_story', 'check_epic_stories'")
    data: Optional[str] = Field(None, description="JSON string of data (for save/add actions)")
    epic_id: Optional[str] = Field(None, description="Epic ID to check stories for")


class FlowDocumentationTool(BaseTool):
    name: str = "Documentation Manager Tool"
    description: str = """
    Tool to manage documentation (Product Brief, Epics, Stories). Use this to:
    - Save Product Brief: action='save_brief', data='{"product_summary": "...", "problem_statement": "...", "target_users": "...", "product_goals": "...", "scope": "...", "revision_count": 0}'
    - Get Product Brief: action='get_brief'
    - Validate Product Brief: action='validate_brief' - Check if all required fields are filled
    - Add Epic: action='add_epic', data='{"id": "epic-1", "name": "...", "description": "...", "domain": "..."}'
    - Add Story: action='add_story', data='{"epic_id": "epic-1" or "independent", "title": "...", "description": "...", "acceptance_criteria": [...]}'
    - Check epic stories: action='check_epic_stories', epic_id='epic-1' - Check if an epic has stories
    - Validate epic-story structure: action='validate_epic_story' - Validate all epics have stories
    - Get documentation: action='get_documentation'

    IMPORTANT: Stories can be independent (epic_id="independent") or belong to an epic.
    Epics MUST have at least 1 story. Use validate_epic_story to check before finalizing.
    Product Brief MUST have all 5 required fields filled. Use validate_brief to check.
    """
    args_schema: Type[BaseModel] = DocumentationToolInput
    flow: Any = Field(default=None, exclude=True)

    def __init__(self, flow: Any, **kwargs):
        super().__init__(**kwargs)
        object.__setattr__(self, 'flow', flow)

    def _run(self, action: str, data: Optional[str] = None, epic_id: Optional[str] = None) -> str:
        """Execute the tool action"""

        if action == "validate_brief":
            # Use the flow state's validation method
            return self.flow.state.get_brief_missing_info()

        elif action == "check_epic_stories":
            if not epic_id:
                return "Error: 'check_epic_stories' requires 'epic_id'"

            # Find stories for this epic
            stories = [s for s in self.flow.state.documentation["stories"] if s.get('epic_id') == epic_id]

            if not stories:
                return f"WARNING: Epic '{epic_id}' has NO stories. Epics must have at least 1 story."
            else:
                return f"Epic '{epic_id}' has {len(stories)} story/stories. ✓"

        elif action == "validate_epic_story":
            epics = self.flow.state.documentation["epics"]
            stories = self.flow.state.documentation["stories"]

            if not epics:
                return "No epics to validate. Validation passed (independent stories allowed)."

            validation_results = []
            epics_without_stories = []

            for epic in epics:
                epic_id = epic.get('id')
                epic_name = epic.get('name', 'Unnamed')

                # Find stories for this epic
                epic_stories = [s for s in stories if s.get('epic_id') == epic_id]

                if not epic_stories:
                    epics_without_stories.append(f"- {epic_name} (ID: {epic_id})")
                    validation_results.append(f"❌ Epic '{epic_name}' has NO stories")
                else:
                    validation_results.append(f"✓ Epic '{epic_name}' has {len(epic_stories)} story/stories")

            # Summary
            independent_stories = [s for s in stories if s.get('epic_id') == 'independent']

            summary = "\n".join(validation_results)
            summary += f"\n\nIndependent Stories: {len(independent_stories)}"

            if epics_without_stories:
                summary += f"\n\n⚠️ VALIDATION FAILED:\nThe following epics have NO stories:\n" + "\n".join(epics_without_stories)
                summary += "\n\nRECOMMENDATION: Either add stories to these epics or remove them."
                return summary
            else:
                summary += "\n\n✅ VALIDATION PASSED: All epics have at least 1 story."
                return summary

        elif action == "save_brief":
            if not data:
                return "Error: 'save_brief' requires 'data'"

            try:
                brief_data = json.loads(data)
                print(f"\n[TOOL DEBUG] Before saving brief: {self.flow.state.documentation['product_brief']}")
                self.flow.state.documentation["product_brief"] = {
                    "product_summary": brief_data.get("product_summary", ""),
                    "problem_statement": brief_data.get("problem_statement", ""),
                    "target_users": brief_data.get("target_users", ""),
                    "product_goals": brief_data.get("product_goals", ""),
                    "scope": brief_data.get("scope", ""),
                    "revision_count": brief_data.get("revision_count", 0)
                }
                print(f"[TOOL DEBUG] After saving brief: {self.flow.state.documentation['product_brief']}")
                print(f"[TOOL DEBUG] Brief has product_summary: {bool(self.flow.state.documentation['product_brief'].get('product_summary'))}")
                return "Successfully saved Product Brief"
            except json.JSONDecodeError as e:
                return f"Error: Invalid JSON in data: {e}"

        elif action == "get_brief":
            print(f"\n[TOOL DEBUG] Getting brief from state: {self.flow.state.documentation['product_brief']}")
            brief = self.flow.state.documentation["product_brief"]
            print(f"[TOOL DEBUG] Brief has product_summary: {bool(brief.get('product_summary') if brief else False)}")
            if brief and brief.get("product_summary"):
                return json.dumps(brief, indent=2)
            else:
                return "No Product Brief found"

        elif action == "add_epic":
            if not data:
                return "Error: 'add_epic' requires 'data'"

            try:
                epic_data = json.loads(data)
                self.flow.state.documentation["epics"].append(epic_data)
                return f"Successfully added Epic: {epic_data.get('name', 'Unnamed')}"
            except json.JSONDecodeError as e:
                return f"Error: Invalid JSON in data: {e}"

        elif action == "add_story":
            if not data:
                return "Error: 'add_story' requires 'data'"

            try:
                story_data = json.loads(data)
                self.flow.state.documentation["stories"].append(story_data)
                return f"Successfully added Story: {story_data.get('title', 'Untitled')}"
            except json.JSONDecodeError as e:
                return f"Error: Invalid JSON in data: {e}"

        elif action == "get_documentation":
            brief_text = self.flow.state.get_product_brief_text()
            backlog_text = self.flow.state.get_backlog_text()
            return f"{brief_text}\n\n{'='*70}\n\n{backlog_text}"

        else:
            return f"Error: Unknown action '{action}'. Valid actions: save_brief, get_brief, add_epic, add_story, get_documentation"


# ==================== LEGACY: For backward compatibility with old crew.py ====================

class DocumentationTool(BaseTool):
    """
    Legacy DocumentationTool for backward compatibility with old crew.py
    Works with ConversationState (manual JSON state)
    """
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
    state_manager: Any = Field(default=None, exclude=True)

    def __init__(self, state_manager: Any, **kwargs):
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
