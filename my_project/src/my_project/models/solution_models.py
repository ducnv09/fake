"""
Pydantic models for solution design outputs
These models define the structure of screens, services, and flows
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class NavigationInfo(BaseModel):
    """Navigation information for a screen"""
    from_screens: List[str] = Field(
        default_factory=list,
        description="Screens that can navigate to this screen",
        alias="from"
    )
    to_screens: List[str] = Field(
        default_factory=list,
        description="Screens this screen can navigate to",
        alias="to"
    )

    class Config:
        populate_by_name = True


class ScreenDesign(BaseModel):
    """Single screen/page design"""
    name: str = Field(..., description="Screen name (e.g., 'Home Page', 'Product Detail Page')")
    purpose: str = Field(..., description="What this screen does from a business perspective")
    user_can: List[str] = Field(..., description="Actions users can perform on this screen")
    navigation: NavigationInfo = Field(..., description="Navigation to/from this screen")


class ScreensOutput(BaseModel):
    """Output model for screens design task"""
    screens: List[ScreenDesign] = Field(..., description="List of all screens/pages in the solution")


class ServiceDesign(BaseModel):
    """Single backend service design"""
    name: str = Field(..., description="Service name (e.g., 'Product Management Service')")
    purpose: str = Field(..., description="What this service does from a business perspective")
    responsibilities: List[str] = Field(..., description="Business responsibilities of this service")
    supports_screens: List[str] = Field(..., description="Screens that use this service")


class ServicesOutput(BaseModel):
    """Output model for services design task"""
    services: List[ServiceDesign] = Field(..., description="List of all backend services in the solution")


class FlowDesign(BaseModel):
    """Single business flow design"""
    name: str = Field(..., description="Flow name (e.g., 'Book Purchase Flow')")
    description: str = Field(..., description="What this flow accomplishes")
    steps: List[str] = Field(..., description="Ordered steps in the flow")
    actors: List[str] = Field(..., description="Actors involved in this flow (users, systems)")


class FlowsOutput(BaseModel):
    """Output model for flows design task"""
    business_flows: List[FlowDesign] = Field(..., description="List of all business flows in the solution")
