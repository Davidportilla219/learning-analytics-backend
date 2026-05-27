"""
Logging utilities for the Learning Analytics Platform.
"""

import logging
import os
import sys
from typing import Optional
from uuid import uuid4

from shared.contracts.enums import LogLevel, ServiceName


class CorrelationFilter(logging.Filter):
    """Filter to add correlation ID to log records."""
    
    def filter(self, record):
        correlation_id = getattr(record, 'correlation_id', None)
        if correlation_id:
            record.correlation_id = correlation_id
        else:
            record.correlation_id = str(uuid4())
        return True


def setup_logging(
    service_name: ServiceName,
    level: LogLevel = LogLevel.INFO,
    correlation_id: Optional[str] = None
) -> logging.Logger:
    """Setup structured logging for a service."""
    
    # Create logger
    logger = logging.getLogger(service_name.value)
    logger.setLevel(getattr(logging, level.value))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(correlation_id)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(CorrelationFilter())
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    
    return logger


def get_logger(service_name: ServiceName) -> logging.Logger:
    """Get a logger for a specific service."""
    return logging.getLogger(service_name.value)


def log_request(logger: logging.Logger, method: str, url: str, status_code: int, correlation_id: str):
    """Log HTTP request information."""
    logger.info(
        f"HTTP {method} {url} - {status_code}",
        extra={'correlation_id': correlation_id}
    )


def log_error(logger: logging.Logger, error: Exception, correlation_id: str):
    """Log error information."""
    logger.error(
        f"Error occurred: {str(error)}",
        extra={'correlation_id': correlation_id},
        exc_info=True
    )


def log_message_processed(
    logger: logging.Logger,
    queue_name: str,
    message_id: str,
    action: str,
    correlation_id: str
):
    """Log message processing information."""
    logger.info(
        f"Message processed - Queue: {queue_name}, Message ID: {message_id}, Action: {action}",
        extra={'correlation_id': correlation_id}
    )


def log_event_received(
    logger: logging.Logger,
    event_type: str,
    student_id: str,
    correlation_id: str
):
    """Log event reception information."""
    logger.info(
        f"Event received - Type: {event_type}, Student: {student_id}",
        extra={'correlation_id': correlation_id}
    )