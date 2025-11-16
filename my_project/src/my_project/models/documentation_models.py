"""
Pydantic models for documentation outputs (Product Brief, Epics, Stories)
"""

from pydantic import BaseModel, Field
from typing import List


class ProductBriefData(BaseModel):
    """Product Brief document structure"""
    product_summary: str = Field(
        ...,
        description="Brief overview (2-3 sentences). Use clear, concise language."
    )
    problem_statement: str = Field(
        ...,
        description="What problem does this solve? Why is it needed? Write in short paragraphs (max 3-4 sentences each) separated by newlines for readability."
    )
    target_users: str = Field(
        ...,
        description="Who will use this product? What are their needs? Format as numbered list or bullet points, one user group per line."
    )
    product_goals: str = Field(
        ...,
        description="What are the key objectives and success criteria? Format as numbered list with clear goals. Use bullet points (-) for sub-items."
    )
    scope: str = Field(
        ...,
        description="What's IN SCOPE and what's OUT OF SCOPE? Format clearly with IN SCOPE and OUT OF SCOPE sections."
    )
    revision_count: int = Field(
        default=0,
        description="Number of revisions made to this brief"
    )


class EpicData(BaseModel):
    """Single Epic structure"""
    id: str = Field(..., description="Epic ID (e.g., 'epic-1', 'epic-2')")
    name: str = Field(..., description="Epic name")
    description: str = Field(..., description="What this epic delivers")
    domain: str = Field(..., description="Feature domain (Product/Cart/Order/Payment/etc)")


class StoryData(BaseModel):
    """Single User Story structure"""
    epic_id: str = Field(..., description="ID of the epic this story belongs to")
    title: str = Field(
        ...,
        description="Story title in format: 'As a [role], I want [feature] so that [benefit]'"
    )
    description: str = Field(..., description="Detailed description of the story")
    acceptance_criteria: List[str] = Field(
        ...,
        description="List of acceptance criteria in Given-When-Then format"
    )


class BacklogOutput(BaseModel):
    """Combined output model for backlog creation - contains both epics and stories"""
    epics: List[EpicData] = Field(..., description="List of all epics organized by feature domain")
    stories: List[StoryData] = Field(..., description="List of all user stories with acceptance criteria")
