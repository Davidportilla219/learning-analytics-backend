"""
Shared contracts for the Learning Analytics Platform.
"""

from .events import (
    BaseEvent,
    ProcessedEvent,
    RiskAlert,
    EventTypes,
    RiskLevels
)

from .dtos import (
    EventSubmissionDTO,
    RiskPredictionDTO,
    AlertResponseDTO
)

from .enums import (
    EventType,
    RiskLevel,
    AlertStatus
)

__all__ = [
    # Events
    'BaseEvent',
    'ProcessedEvent', 
    'RiskAlert',
    'EventTypes',
    'RiskLevels',
    
    # DTOs
    'EventSubmissionDTO',
    'RiskPredictionDTO',
    'AlertResponseDTO',
    
    # Enums
    'EventType',
    'RiskLevel',
    'AlertStatus'
]