"""
Models package for solution design and documentation outputs
"""

from .solution_models import (
    ScreenDesign,
    ScreensOutput,
    ServiceDesign,
    ServicesOutput,
    FlowDesign,
    FlowsOutput,
    NavigationInfo
)

from .documentation_models import (
    ProductBriefData,
    EpicData,
    StoryData,
    BacklogOutput
)

__all__ = [
    # Solution models
    'ScreenDesign',
    'ScreensOutput',
    'ServiceDesign',
    'ServicesOutput',
    'FlowDesign',
    'FlowsOutput',
    'NavigationInfo',
    # Documentation models
    'ProductBriefData',
    'EpicData',
    'StoryData',
    'BacklogOutput'
]
