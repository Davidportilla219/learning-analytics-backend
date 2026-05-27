"""
Event processing service with RabbitMQ integration.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import pika
from pika.exceptions import AMQPConnectionError, AMQPChannelError

from app.core.config import settings
from app.models.event import Event

logger = logging.getLogger(__name__)


class EventProcessor:
    """Service for processing events and publishing to RabbitMQ."""
    
    def __init__(self):
        self.connection = None
        self.channel = None
        self._connected = False
        self._reconnect_attempts = 0
        self._max_reconnect_attempts = 5
        self._reconnect_delay = 5  # seconds
    
    async def initialize(self):
        """Initialize RabbitMQ connection."""
        try:
            await self._connect_rabbitmq()
            logger.info("Event processor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize event processor: {e}")
            raise
    
    async def _connect_rabbitmq(self):
        """Connect to RabbitMQ."""
        try:
            # Create connection parameters
            credentials = pika.PlainCredentials(
                settings.RABBITMQ_USER,
                settings.RABBITMQ_PASSWORD
            )
            
            parameters = pika.ConnectionParameters(
                host=settings.RABBITMQ_HOST,
                port=settings.RABBITMQ_PORT,
                credentials=credentials,
                connection_attempts=3,
                retry_delay=5,
                heartbeat=60,
                blocked_connection_timeout=30
            )
            
            # Connect to RabbitMQ
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare exchange
            self.channel.exchange_declare(
                exchange=settings.RABBITMQ_EXCHANGE,
                exchange_type='direct',
                durable=True
            )
            
            # Declare queue
            self.channel.queue_declare(
                queue=settings.RABBITMQ_QUEUE,
                durable=True,
                arguments={
                    'x-message-ttl': 3600000,  # 1 hour message TTL
                    'x-dead-letter-exchange': settings.RABBITMQ_EXCHANGE,
                    'x-dead-letter-routing-key': 'failed_events'
                }
            )
            
            # Bind queue to exchange
            self.channel.queue_bind(
                queue=settings.RABBITMQ_QUEUE,
                exchange=settings.RABBITMQ_EXCHANGE,
                routing_key='learning_events'
            )
            
            self._connected = True
            self._reconnect_attempts = 0
            logger.info("Connected to RabbitMQ successfully")
            
        except AMQPConnectionError as e:
            logger.error(f"RabbitMQ connection error: {e}")
            await self._handle_connection_error()
        except Exception as e:
            logger.error(f"Unexpected error connecting to RabbitMQ: {e}")
            await self._handle_connection_error()
    
    async def _handle_connection_error(self):
        """Handle RabbitMQ connection errors."""
        self._connected = False
        
        if self._reconnect_attempts < self._max_reconnect_attempts:
            self._reconnect_attempts += 1
            logger.warning(
                f"RabbitMQ connection failed. "
                f"Attempt {self._reconnect_attempts}/{self._max_reconnect_attempts}. "
                f"Reconnecting in {self._reconnect_delay} seconds..."
            )
            
            await asyncio.sleep(self._reconnect_delay)
            await self._connect_rabbitmq()
        else:
            logger.error(
                f"Max reconnection attempts ({self._max_reconnect_attempts}) reached. "
                "Event processor will continue without RabbitMQ."
            )
    
    async def process_event(self, event: Event):
        """Process a single event and publish to RabbitMQ."""
        try:
            # Validate event
            if not self._validate_event(event):
                logger.warning(f"Invalid event: {event.event_id}")
                return
            
            # Transform event for processing
            processed_event = self._transform_event(event)
            
            # Publish to RabbitMQ
            if self._connected:
                await self._publish_to_rabbitmq(processed_event)
                logger.info(f"Published event {event.event_id} to RabbitMQ")
            else:
                logger.warning(
                    f"RabbitMQ not connected. Event {event.event_id} will be processed locally"
                )
                # TODO: Implement local processing fallback
            
            # Log successful processing
            self._log_event_processing(event, "success")
            
        except Exception as e:
            logger.error(f"Error processing event {event.event_id}: {e}")
            self._log_event_processing(event, "error", str(e))
    
    def _validate_event(self, event: Event) -> bool:
        """Validate event before processing."""
        if not event.event_id:
            logger.error("Event ID is required")
            return False
        
        if not event.event_type:
            logger.error("Event type is required")
            return False
        
        if not event.user_id:
            logger.error("User ID is required")
            return False
        
        if not event.timestamp:
            logger.error("Timestamp is required")
            return False
        
        return True
    
    def _transform_event(self, event: Event) -> Dict[str, Any]:
        """Transform event for processing."""
        return {
            "event_id": event.event_id,
            "event_type": event.event_type,
            "user_id": event.user_id,
            "session_id": event.session_id,
            "course_id": event.course_id,
            "timestamp": event.timestamp.isoformat(),
            "data": event.data,
            "metadata": event.event_metadata or {},
            "processed_at": datetime.now().isoformat(),
            "service": "event-capture-service"
        }
    
    async def _publish_to_rabbitmq(self, event: Dict[str, Any]):
        """Publish event to RabbitMQ."""
        try:
            # Convert event to JSON
            message = json.dumps(event, default=str)
            
            # Publish message
            self.channel.basic_publish(
                exchange=settings.RABBITMQ_EXCHANGE,
                routing_key='learning_events',
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    content_type='application/json',
                    message_id=event['event_id']
                )
            )
            
        except AMQPChannelError as e:
            logger.error(f"RabbitMQ channel error: {e}")
            await self._handle_connection_error()
            # Retry publishing after reconnection
            if self._connected:
                await self._publish_to_rabbitmq(event)
        except Exception as e:
            logger.error(f"Error publishing to RabbitMQ: {e}")
            raise
    
    def _log_event_processing(self, event: Event, status: str, error: Optional[str] = None):
        """Log event processing status."""
        log_data = {
            "event_id": event.event_id,
            "event_type": event.event_type,
            "user_id": event.user_id,
            "status": status,
            "processed_at": datetime.now().isoformat()
        }
        
        if error:
            log_data["error"] = error
        
        if status == "success":
            logger.info(f"Event processing successful: {log_data}")
        elif status == "error":
            logger.error(f"Event processing failed: {log_data}")
        else:
            logger.warning(f"Event processing warning: {log_data}")
    
    async def close(self):
        """Close RabbitMQ connection."""
        try:
            if self.channel:
                self.channel.close()
            if self.connection:
                self.connection.close()
            logger.info("RabbitMQ connection closed")
        except Exception as e:
            logger.error(f"Error closing RabbitMQ connection: {e}")
    
    async def publish_batch(self, events: list):
        """Publish multiple events in batch."""
        if not events:
            return
        
        try:
            # Process and publish each event
            for event in events:
                await self.process_event(event)
            
            logger.info(f"Published batch of {len(events)} events")
            
        except Exception as e:
            logger.error(f"Error publishing batch events: {e}")
            raise
    
    async def get_queue_status(self) -> Dict[str, Any]:
        """Get RabbitMQ queue status."""
        try:
            if not self._connected:
                return {"status": "disconnected"}
            
            # Get queue information
            method_frame = self.channel.queue_declare(
                queue=settings.RABBITMQ_QUEUE,
                passive=True
            )
            
            return {
                "status": "connected",
                "queue": settings.RABBITMQ_QUEUE,
                "message_count": method_frame.method.message_count,
                "consumer_count": method_frame.method.consumer_count
            }
            
        except Exception as e:
            logger.error(f"Error getting queue status: {e}")
            return {"status": "error", "error": str(e)}


# Global event processor instance
event_processor = EventProcessor()