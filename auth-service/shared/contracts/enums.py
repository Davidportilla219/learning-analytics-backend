"""
Enumerations for the Learning Analytics Platform.
"""

from enum import Enum


class EventType(str, Enum):
    """Educational event types."""
    EXERCISE_SUBMITTED = "exercise_submitted"
    QUIZ_COMPLETED = "quiz_completed"
    VIDEO_WATCHED = "video_watched"
    FORUM_POST = "forum_post"
    ASSIGNMENT_SUBMITTED = "assignment_submitted"
    LOGIN = "login"
    LOGOUT = "logout"
    COURSE_ENROLLED = "course_enrolled"
    COURSE_COMPLETED = "course_completed"


class RiskLevel(str, Enum):
    """Risk level classification."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class AlertStatus(str, Enum):
    """Alert status enumeration."""
    ACTIVE = "ACTIVE"
    RESOLVED = "RESOLVED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    ESCALATED = "ESCALATED"


class ServiceName(str, Enum):
    """Service names for logging and monitoring."""
    API_GATEWAY = "api-gateway"
    AUTH_SERVICE = "auth-service"
    EVENT_CAPTURE_SERVICE = "event-capture-service"
    TELEMETRY_PROCESSOR_SERVICE = "telemetry-processor-service"
    ACADEMIC_RISK_SERVICE = "academic-risk-service"
    ALERT_SERVICE = "alert-service"


class QueueName(str, Enum):
    """RabbitMQ queue names."""
    RAW_EVENTS = "raw-events"
    PROCESSED_EVENTS = "processed-events"
    RISK_ALERTS = "risk-alerts"
    
    # Dead Letter Queues
    RAW_EVENTS_DLQ = "raw-events.dlq"
    PROCESSED_EVENTS_DLQ = "processed-events.dlq"
    RISK_ALERTS_DLQ = "risk-alerts.dlq"


class LogLevel(str, Enum):
    """Log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class HTTPStatus(str, Enum):
    """HTTP status codes."""
    OK = "200"
    CREATED = "201"
    BAD_REQUEST = "400"
    UNAUTHORIZED = "401"
    FORBIDDEN = "403"
    NOT_FOUND = "404"
    INTERNAL_SERVER_ERROR = "500"
    SERVICE_UNAVAILABLE = "503"


class MessageAction(str, Enum):
    """Message processing actions."""
    PROCESS = "process"
    RETRY = "retry"
    DEAD_LETTER = "dead_letter"
    ACKNOWLEDGE = "acknowledge"