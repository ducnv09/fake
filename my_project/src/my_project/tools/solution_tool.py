"""
Custom tool for agents to interact with solution components
Updated to work with CrewAI Flow instead of manual ConversationState
"""

from crewai.tools import BaseTool
from typing import Type, Optional, Any
from pydantic import BaseModel, Field
import json


class SolutionToolInput(BaseModel):
    """Input schema for FlowSolutionTool"""
    action: str = Field(..., description="Action to perform: 'add_screen', 'add_service', 'add_flow', 'get_solution', 'get_summary', 'check_complete'")
    component_data: Optional[str] = Field(None, description="JSON string of component data (for add actions)")


class FlowSolutionTool(BaseTool):
    name: str = "Solution Manager Tool"
    description: str = """
    Tool to manage BUSINESS-LEVEL solution components (NOT technical implementation). Use this to:
    - Add screen/page: action='add_screen', component_data='{"name": "Home Page", "purpose": "Landing page for users", "user_can": ["Browse items", "Search"], "navigation": {"from": [...], "to": [...]}}'
    - Add backend service: action='add_service', component_data='{"name": "Product Management Service", "purpose": "Manage product catalog", "responsibilities": ["Maintain products", "Track inventory"], "supports_screens": [...]}'
    - Add business flow: action='add_flow', component_data='{"name": "Purchase Flow", "description": "...", "steps": [...], "actors": [...]}'
    - Get solution: action='get_solution'
    - Get summary: action='get_summary'
    - Check if solution complete: action='check_complete'

    IMPORTANT: Focus on BUSINESS aspects, NOT technical implementation (no HTTP endpoints, no database schemas, no framework details)
    """
    args_schema: Type[BaseModel] = SolutionToolInput
    flow: Any = Field(default=None, exclude=True)

    def __init__(self, flow: Any, **kwargs):
        super().__init__(**kwargs)
        object.__setattr__(self, 'flow', flow)

    def _run(self, action: str, component_data: Optional[str] = None) -> str:
        """Execute the tool action"""

        if action == "add_screen":
            if not component_data:
                return "Error: 'add_screen' requires 'component_data'"

            try:
                component = json.loads(component_data)
                self.flow.state.solution["screens"].append(component)
                return f"Successfully added screen: {component.get('name', 'Unnamed')}"
            except json.JSONDecodeError as e:
                return f"Error: Invalid JSON in component_data: {e}"

        elif action == "add_service":
            if not component_data:
                return "Error: 'add_service' requires 'component_data'"

            try:
                component = json.loads(component_data)
                self.flow.state.solution["services"].append(component)
                return f"Successfully added service: {component.get('name', 'Unnamed')}"
            except json.JSONDecodeError as e:
                return f"Error: Invalid JSON in component_data: {e}"

        elif action == "add_flow":
            if not component_data:
                return "Error: 'add_flow' requires 'component_data'"

            try:
                flow_data = json.loads(component_data)
                self.flow.state.solution["business_flows"].append(flow_data)
                return f"Successfully added business flow: {flow_data.get('name', 'Unnamed')}"
            except json.JSONDecodeError as e:
                return f"Error: Invalid JSON in component_data: {e}"

        elif action == "get_solution":
            return self.flow.state.get_solution_text()

        elif action == "get_summary":
            screens_count = len(self.flow.state.solution["screens"])
            services_count = len(self.flow.state.solution["services"])
            flows_count = len(self.flow.state.solution["business_flows"])

            summary = f"""Solution Components:
- Screens/Pages: {screens_count} items
- Backend Services: {services_count} items
- Business Flows: {flows_count} items

Total Solution Elements: {screens_count + services_count + flows_count}"""
            return summary

        elif action == "check_complete":
            screens_count = len(self.flow.state.solution["screens"])
            services_count = len(self.flow.state.solution["services"])
            flows_count = len(self.flow.state.solution["business_flows"])
            total_count = screens_count + services_count + flows_count

            # Check completeness criteria
            if screens_count >= 3 and services_count >= 2 and flows_count >= 2:
                status = "COMPLETE"
                reason = f"Sufficient solution components: {screens_count} screens, {services_count} services, {flows_count} flows"
            elif total_count >= 7:
                status = "COMPLETE"
                reason = f"Total of {total_count} solution components defined"
            else:
                status = "INCOMPLETE"
                missing = []
                if screens_count < 3:
                    missing.append(f"screens ({screens_count}/3)")
                if services_count < 2:
                    missing.append(f"services ({services_count}/2)")
                if flows_count < 2:
                    missing.append(f"business flows ({flows_count}/2)")
                reason = f"Need more: {', '.join(missing)}"

            return f"Solution Status: {status}\nReason: {reason}"

        else:
            return f"Error: Unknown action '{action}'. Valid actions: add_screen, add_service, add_flow, get_solution, get_summary, check_complete"


# ==================== LEGACY: For backward compatibility with old crew.py ====================

class SolutionTool(BaseTool):
    """
    Legacy SolutionTool for backward compatibility with old crew.py
    Works with ConversationState (manual JSON state)
    """
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
    state_manager: Any = Field(default=None, exclude=True)

    def __init__(self, state_manager: Any, **kwargs):
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
