"""
Custom tool for agents to interact with users via choices/options
Similar to Claude Code's AskUserQuestion functionality
"""

from crewai.tools import BaseTool
from typing import Type, Optional, Any, List, Dict
from pydantic import BaseModel, Field
import json


class UserInteractionInput(BaseModel):
    """Input schema for FlowUserInteractionTool"""
    action: str = Field(..., description="Action to perform: 'present_options', 'get_last_choice', 'check_pending'")
    question: Optional[str] = Field(None, description="The question to ask the user")
    options: Optional[str] = Field(None, description="JSON string of options list: [{'label': '...', 'value': '...', 'description': '...'}, ...]")
    context: Optional[str] = Field(None, description="Context/category for this question (e.g., 'technology_choice', 'architecture_pattern')")


class FlowUserInteractionTool(BaseTool):
    name: str = "User Interaction Tool"
    description: str = """
    Tool to interact with users through choice-based questions. Use this to:
    - Present options to user: action='present_options', question='Which framework?', options='[{"label": "React", "value": "react", "description": "Popular UI library"}, ...]', context='frontend_framework'
    - Get last user choice: action='get_last_choice', context='frontend_framework' (optional)
    - Check if there's a pending question: action='check_pending'

    This tool allows agents to get user input when making decisions about technologies, architectures, or approaches.
    """
    args_schema: Type[BaseModel] = UserInteractionInput
    flow: Any = Field(default=None, exclude=True)

    def __init__(self, flow: Any, **kwargs):
        super().__init__(**kwargs)
        object.__setattr__(self, 'flow', flow)

    def _run(self, action: str, question: Optional[str] = None, options: Optional[str] = None, context: Optional[str] = None) -> str:
        """Execute the tool action"""

        if action == "present_options":
            if not question or not options:
                return "Error: 'present_options' requires 'question' and 'options'"

            try:
                options_list = json.loads(options)

                # Validate options format
                if not isinstance(options_list, list) or len(options_list) < 2:
                    return "Error: 'options' must be a JSON list with at least 2 items"

                for opt in options_list:
                    if not isinstance(opt, dict) or 'label' not in opt or 'value' not in opt:
                        return "Error: Each option must be a dict with 'label' and 'value' keys"

                # Store the pending question in state
                pending_question = {
                    "question": question,
                    "options": options_list,
                    "context": context or "general",
                    "timestamp": None  # Will be set when displayed to user
                }

                self.flow.state.pending_user_question = pending_question

                return f"SUCCESS: Question prepared and waiting for user response.\nQuestion: {question}\nOptions: {len(options_list)} choices\nContext: {context or 'general'}"

            except json.JSONDecodeError as e:
                return f"Error: Invalid JSON in options: {e}"

        elif action == "get_last_choice":
            # Get the last user choice from the specified context or most recent
            if not self.flow.state.user_choices:
                return "No user choices recorded yet."

            if context:
                # Find the last choice for this context
                matching_choices = [
                    choice for choice in reversed(self.flow.state.user_choices)
                    if choice.get('context') == context
                ]
                if matching_choices:
                    choice = matching_choices[0]
                    return f"Last choice for '{context}':\nSelected: {choice.get('selected_label')} (value: {choice.get('selected_value')})\nTimestamp: {choice.get('timestamp')}"
                else:
                    return f"No choices found for context: {context}"
            else:
                # Return the most recent choice
                choice = self.flow.state.user_choices[-1]
                return f"Most recent user choice:\nContext: {choice.get('context')}\nSelected: {choice.get('selected_label')} (value: {choice.get('selected_value')})\nTimestamp: {choice.get('timestamp')}"

        elif action == "check_pending":
            if self.flow.state.pending_user_question:
                q = self.flow.state.pending_user_question
                return f"PENDING QUESTION:\nQuestion: {q.get('question')}\nContext: {q.get('context')}\nOptions: {len(q.get('options', []))} choices"
            else:
                return "No pending questions. Flow can continue."

        else:
            return f"Error: Unknown action '{action}'. Valid actions: present_options, get_last_choice, check_pending"
