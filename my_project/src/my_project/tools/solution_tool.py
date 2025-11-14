"""
Custom tool for agents to interact with solution components
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


class SolutionToolInput(BaseModel):
    """Input schema for SolutionTool"""
    action: str = Field(..., description="Action to perform: 'add_frontend', 'add_backend', 'add_flow', 'get_solution', 'get_summary', 'check_complete'")
    component_data: Optional[str] = Field(None, description="JSON string of component data (for add actions)")


class SolutionTool(BaseTool):
    name: str = "Solution Manager Tool"
    description: str = """
    Tool to manage solution components. Use this to:
    - Add frontend component: action='add_frontend', component_data='{"name": "...", "description": "...", "features": [...], "user_interactions": [...]}'
    - Add backend component: action='add_backend', component_data='{"name": "...", "description": "...", "endpoints": [...], "business_logic": [...], "data_models": [...]}'
    - Add business flow: action='add_flow', component_data='{"name": "...", "description": "...", "steps": [...], "actors": [...]}'
    - Get solution: action='get_solution'
    - Get summary: action='get_summary'
    - Check if solution complete: action='check_complete'
    """
    args_schema: Type[BaseModel] = SolutionToolInput
    state_manager: ConversationState = Field(default=None, exclude=True)

    def __init__(self, state_manager: ConversationState, **kwargs):
        super().__init__(**kwargs)
        object.__setattr__(self, 'state_manager', state_manager)

    def _run(self, action: str, component_data: Optional[str] = None) -> str:
        """Execute the tool action"""

        if action == "add_frontend":
            if not component_data:
                return "Error: 'add_frontend' requires 'component_data'"

            try:
                component = json.loads(component_data)
                success = self.state_manager.add_frontend_component(component)
                if success:
                    return f"Successfully added frontend component: {component.get('name', 'Unnamed')}"
                else:
                    return "Failed to add frontend component"
            except json.JSONDecodeError as e:
                return f"Error: Invalid JSON in component_data: {e}"

        elif action == "add_backend":
            if not component_data:
                return "Error: 'add_backend' requires 'component_data'"

            try:
                component = json.loads(component_data)
                success = self.state_manager.add_backend_component(component)
                if success:
                    return f"Successfully added backend component: {component.get('name', 'Unnamed')}"
                else:
                    return "Failed to add backend component"
            except json.JSONDecodeError as e:
                return f"Error: Invalid JSON in component_data: {e}"

        elif action == "add_flow":
            if not component_data:
                return "Error: 'add_flow' requires 'component_data'"

            try:
                flow = json.loads(component_data)
                success = self.state_manager.add_business_flow(flow)
                if success:
                    return f"Successfully added business flow: {flow.get('name', 'Unnamed')}"
                else:
                    return "Failed to add business flow"
            except json.JSONDecodeError as e:
                return f"Error: Invalid JSON in component_data: {e}"

        elif action == "get_solution":
            return self.state_manager.get_solution_text()

        elif action == "get_summary":
            return self.state_manager.get_solution_summary()

        elif action == "check_complete":
            is_complete, reason = self.state_manager.is_solution_complete()
            status = "COMPLETE" if is_complete else "INCOMPLETE"
            return f"Solution Status: {status}\nReason: {reason}"

        else:
            return f"Error: Unknown action '{action}'. Valid actions: add_frontend, add_backend, add_flow, get_solution, get_summary, check_complete"
