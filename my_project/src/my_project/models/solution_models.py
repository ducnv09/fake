"""
Pydantic models for solution design outputs
Focuses on business flows and user journeys only
"""

from pydantic import BaseModel, Field
from typing import List


class FlowDesign(BaseModel):
    """Single business flow design"""
    name: str = Field(..., description="Flow name (e.g., 'Book Purchase Flow')")
    description: str = Field(..., description="What this flow accomplishes")
    steps: List[str] = Field(..., description="Ordered steps in the flow")
    actors: List[str] = Field(..., description="Actors involved in this flow (users, systems)")


class FlowsOutput(BaseModel):
    """Output model for flows design task"""
    business_flows: List[FlowDesign] = Field(..., description="List of all business flows in the solution")
