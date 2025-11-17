"""
Pydantic models for documentation outputs (Product Brief, Epics, Stories)
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal


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
    status: str = Field(
        default="Planned",
        description="Epic status: Planned/In Progress/Completed"
    )


class StoryData(BaseModel):
    """Single User Story structure with INVEST principles"""
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

    # INVEST principle fields
    story_points: int = Field(
        ...,
        description="Effort estimation using Fibonacci scale (1,2,3,5,8,13). 1=1 day, 3=3 days, 5=1 week, 8=2 weeks. REQUIRED for INVEST compliance."
    )
    priority: Literal["High", "Medium", "Low"] = Field(
        default="Medium",
        description="Story priority: High (must have), Medium (should have), Low (nice to have)"
    )
    dependencies: List[str] = Field(
        default_factory=list,
        description="List of story IDs this story depends on. Keep minimal for Independence principle"
    )

    @field_validator('story_points')
    @classmethod
    def validate_fibonacci(cls, v: int) -> int:
        """Validate that story_points follows Fibonacci sequence (INVEST: Estimable)"""
        valid_points = [1, 2, 3, 5, 8, 13]
        if v not in valid_points:
            raise ValueError(
                f"story_points must be one of {valid_points} (Fibonacci scale). "
                f"Got {v}. Use 1-3 for simple tasks, 5 for complex, 8+ should be split."
            )
        if v >= 8:
            # Warning: story is too large (INVEST: Small)
            import warnings
            warnings.warn(
                f"Story with {v} points is very large. Consider splitting into smaller stories. "
                f"INVEST principle 'Small' suggests stories should be completable in 1-2 sprints.",
                UserWarning
            )
        return v

    @field_validator('dependencies')
    @classmethod
    def validate_dependencies(cls, v: List[str]) -> List[str]:
        """Validate that dependencies are minimal (INVEST: Independent)"""
        if len(v) > 3:
            raise ValueError(
                f"Story has {len(v)} dependencies. INVEST 'Independent' principle requires "
                f"minimal dependencies (max 3). Too many dependencies indicate the story "
                f"should be refactored or split."
            )
        return v


class BacklogOutput(BaseModel):
    """Combined output model for backlog creation - contains both epics and stories"""
    epics: List[EpicData] = Field(..., description="List of all epics organized by feature domain")
    stories: List[StoryData] = Field(..., description="List of all user stories with acceptance criteria")
