"""
Test suite for the Event Processor service.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from app.services.event_processor import EventProcessor
from app.models.event import Event, EventCreate


class TestEventProcessor:
    """Test suite for EventProcessor service."""
    
    @pytest.fixture
    def event_processor(self):
        """Create an EventProcessor instance for testing."""
        processor = EventProcessor()
        processor._connected = True  # Mock connected state
        processor.channel = Mock()
        processor.connection = Mock()
        return processor
    
    @pytest.fixture
    def sample_event(self):
        """Create a sample event for testing."""
        return Event(
            id=1,
            event_id="test-event-001",
            event_type="login",
            user_id="user-001",
            session_id="session-001",
            course_id="course-001",
            timestamp=datetime.now(),
            data={"ip_address": "192.168.1.1", "user_agent": "Mozilla/5.0"},
            metadata={"device": "desktop", "browser": "chrome"},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    def test_validate_event_valid(self, sample_event):
        """Test event validation with valid event."""
        processor = EventProcessor()
        assert processor._validate_event(sample_event) is True
    
    def test_validate_event_missing_event_id(self, sample_event):
        """Test event validation with missing event ID."""
        processor = EventProcessor()
        sample_event.event_id = None
        assert processor._validate_event(sample_event) is False
    
    def test_validate_event_missing_event_type(self, sample_event):
        """Test event validation with missing event type."""
        processor = EventProcessor()
        sample_event.event_type = None
        assert processor._validate_event(sample_event) is False
    
    def test_validate_event_missing_user_id(self, sample_event):
        """Test event validation with missing user ID."""
        processor = EventProcessor()
        sample_event.user_id = None
        assert processor._validate_event(sample_event) is False
    
    def test_validate_event_missing_timestamp(self, sample_event):
        """Test event validation with missing timestamp."""
        processor = EventProcessor()
        sample_event.timestamp = None
        assert processor._validate_event(sample_event) is False
    
    def test_transform_event(self, sample_event):
        """Test event transformation."""
        processor = EventProcessor()
        transformed = processor._transform_event(sample_event)
        
        assert transformed["event_id"] == sample_event.event_id
        assert transformed["event_type"] == sample_event.event_type
        assert transformed["user_id"] == sample_event.user_id
        assert transformed["session_id"] == sample_event.session_id
        assert transformed["course_id"] == sample_event.course_id
        assert transformed["timestamp"] == sample_event.timestamp.isoformat()
        assert transformed["data"] == sample_event.data
        assert transformed["metadata"] == sample_event.metadata
        assert "processed_at" in transformed
        assert "service" in transformed
    
    @patch('app.services.event_processor.pika')
    def test_publish_to_rabbitmq_success(self, mock_pika, event_processor):
        """Test successful RabbitMQ publishing."""
        # Mock the channel
        mock_channel = Mock()
        event_processor.channel = mock_channel
        
        # Mock event data
        event_data = {
            "event_id": "test-event-001",
            "event_type": "login",
            "user_id": "user-001",
            "timestamp": datetime.now().isoformat(),
            "data": {"test": "data"},
            "metadata": {},
            "processed_at": datetime.now().isoformat(),
            "service": "event-capture-service"
        }
        
        # Call the method
        asyncio.run(event_processor._publish_to_rabbitmq(event_data))
        
        # Verify the channel method was called
        mock_channel.basic_publish.assert_called_once()
        call_args = mock_channel.basic_publish.call_args
        assert call_args[1]['exchange'] == 'learning_events'
        assert call_args[1]['routing_key'] == 'learning_events'
        assert 'test-event-001' in call_args[1]['body']
    
    @patch('app.services.event_processor.pika')
    def test_publish_to_rabbitmq_channel_error(self, mock_pika, event_processor):
        """Test RabbitMQ publishing with channel error."""
        # Mock the channel to raise an exception
        mock_channel = Mock()
        mock_channel.basic_publish.side_effect = Exception("Channel error")
        event_processor.channel = mock_channel
        
        # Mock event data
        event_data = {
            "event_id": "test-event-001",
            "event_type": "login",
            "user_id": "user-001",
            "timestamp": datetime.now().isoformat(),
            "data": {"test": "data"},
            "metadata": {},
            "processed_at": datetime.now().isoformat(),
            "service": "event-capture-service"
        }
        
        # Call the method and expect it to raise an exception
        with pytest.raises(Exception) as exc_info:
            asyncio.run(event_processor._publish_to_rabbitmq(event_data))
        
        assert "Channel error" in str(exc_info.value)
    
    @patch('app.services.event_processor.pika')
    def test_process_event_success(self, mock_pika, event_processor, sample_event):
        """Test successful event processing."""
        # Mock the channel
        mock_channel = Mock()
        event_processor.channel = mock_channel
        
        # Mock the logger
        with patch('app.services.event_processor.logger') as mock_logger:
            # Call the method
            asyncio.run(event_processor.process_event(sample_event))
            
            # Verify logging
            mock_logger.info.assert_called()
            assert "Published event test-event-001 to RabbitMQ" in str(mock_logger.info.call_args)
    
    @patch('app.services.event_processor.pika')
    def test_process_event_invalid_event(self, mock_pika, event_processor):
        """Test processing invalid event."""
        # Create invalid event
        invalid_event = Event(
            id=1,
            event_id=None,  # Invalid - missing event ID
            event_type="login",
            user_id="user-001",
            session_id="session-001",
            course_id="course-001",
            timestamp=datetime.now(),
            data={"ip_address": "192.168.1.1"},
            metadata={"device": "desktop"},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Mock the logger
        with patch('app.services.event_processor.logger') as mock_logger:
            # Call the method
            asyncio.run(event_processor.process_event(invalid_event))
            
            # Verify warning was logged
            mock_logger.warning.assert_called()
            assert "Invalid event: None" in str(mock_logger.warning.call_args)
    
    @patch('app.services.event_processor.pika')
    def test_process_event_rabbitmq_disconnected(self, mock_pika, event_processor, sample_event):
        """Test event processing when RabbitMQ is disconnected."""
        # Set disconnected state
        event_processor._connected = False
        
        # Mock the logger
        with patch('app.services.event_processor.logger') as mock_logger:
            # Call the method
            asyncio.run(event_processor.process_event(sample_event))
            
            # Verify warning was logged
            mock_logger.warning.assert_called()
            assert "RabbitMQ not connected" in str(mock_logger.warning.call_args)
    
    def test_log_event_processing_success(self, event_processor, sample_event):
        """Test logging successful event processing."""
        with patch('app.services.event_processor.logger') as mock_logger:
            event_processor._log_event_processing(sample_event, "success")
            
            mock_logger.info.assert_called()
            assert "Event processing successful" in str(mock_logger.info.call_args)
            assert "test-event-001" in str(mock_logger.info.call_args)
    
    def test_log_event_processing_error(self, event_processor, sample_event):
        """Test logging event processing error."""
        error_message = "Test error message"
        
        with patch('app.services.event_processor.logger') as mock_logger:
            event_processor._log_event_processing(sample_event, "error", error_message)
            
            mock_logger.error.assert_called()
            assert "Event processing failed" in str(mock_logger.error.call_args)
            assert "test-event-001" in str(mock_logger.error.call_args)
            assert error_message in str(mock_logger.error.call_args)
    
    def test_log_event_processing_warning(self, event_processor, sample_event):
        """Test logging event processing warning."""
        with patch('app.services.event_processor.logger') as mock_logger:
            event_processor._log_event_processing(sample_event, "warning")
            
            mock_logger.warning.assert_called()
            assert "Event processing warning" in str(mock_logger.warning.call_args)
            assert "test-event-001" in str(mock_logger.warning.call_args)
    
    @patch('app.services.event_processor.pika')
    def test_publish_batch(self, mock_pika, event_processor):
        """Test publishing batch of events."""
        # Create sample events
        events = [
            Event(
                id=1,
                event_id="batch-event-001",
                event_type="login",
                user_id="user-001",
                session_id="session-001",
                course_id="course-001",
                timestamp=datetime.now(),
                data={"ip_address": "192.168.1.1"},
                metadata={"device": "desktop"},
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            Event(
                id=2,
                event_id="batch-event-002",
                event_type="page_view",
                user_id="user-001",
                session_id="session-001",
                course_id="course-001",
                timestamp=datetime.now(),
                data={"page": "/dashboard"},
                metadata={"device": "desktop"},
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]
        
        # Mock the channel
        mock_channel = Mock()
        event_processor.channel = mock_channel
        
        # Mock the logger
        with patch('app.services.event_processor.logger') as mock_logger:
            # Call the method
            asyncio.run(event_processor.publish_batch(events))
            
            # Verify logging
            mock_logger.info.assert_called()
            assert "Published batch of 2 events" in str(mock_logger.info.call_args)
    
    @patch('app.services.event_processor.pika')
    def test_publish_batch_empty(self, mock_pika, event_processor):
        """Test publishing empty batch."""
        # Call the method with empty list
        asyncio.run(event_processor.publish_batch([]))
        
        # Should not raise any exception
        # No publishing should occur
    
    @patch('app.services.event_processor.pika')
    def test_publish_batch_error(self, mock_pika, event_processor):
        """Test publishing batch with error."""
        # Create sample events
        events = [
            Event(
                id=1,
                event_id="batch-event-001",
                event_type="login",
                user_id="user-001",
                session_id="session-001",
                course_id="course-001",
                timestamp=datetime.now(),
                data={"ip_address": "192.168.1.1"},
                metadata={"device": "desktop"},
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]
        
        # Mock the channel to raise an exception
        mock_channel = Mock()
        mock_channel.basic_publish.side_effect = Exception("Publish error")
        event_processor.channel = mock_channel
        
        # Mock the logger
        with patch('app.services.event_processor.logger') as mock_logger:
            # Call the method and expect it to raise an exception
            with pytest.raises(Exception) as exc_info:
                asyncio.run(event_processor.publish_batch(events))
            
            assert "Publish error" in str(exc_info.value)
            mock_logger.error.assert_called()
            assert "Error publishing batch events" in str(mock_logger.error.call_args)
    
    def test_get_queue_status_connected(self, event_processor):
        """Test getting queue status when connected."""
        # Mock the channel
        mock_channel = Mock()
        mock_method = Mock()
        mock_method.method.message_count = 10
        mock_method.method.consumer_count = 2
        mock_channel.queue_declare.return_value = mock_method
        event_processor.channel = mock_channel
        
        # Call the method
        status = asyncio.run(event_processor.get_queue_status())
        
        # Verify status
        assert status["status"] == "connected"
        assert status["queue"] == "learning_events"
        assert status["message_count"] == 10
        assert status["consumer_count"] == 2
    
    def test_get_queue_status_disconnected(self, event_processor):
        """Test getting queue status when disconnected."""
        # Set disconnected state
        event_processor._connected = False
        
        # Call the method
        status = asyncio.run(event_processor.get_queue_status())
        
        # Verify status
        assert status["status"] == "disconnected"
    
    @patch('app.services.event_processor.pika')
    def test_get_queue_status_error(self, mock_pika, event_processor):
        """Test getting queue status with error."""
        # Mock the channel to raise an exception
        mock_channel = Mock()
        mock_channel.queue_declare.side_effect = Exception("Queue error")
        event_processor.channel = mock_channel
        
        # Call the method
        status = asyncio.run(event_processor.get_queue_status())
        
        # Verify status
        assert status["status"] == "error"
        assert "Queue error" in status["error"]
    
    def test_close_connection(self, event_processor):
        """Test closing RabbitMQ connection."""
        # Mock the channel and connection
        mock_channel = Mock()
        mock_connection = Mock()
        event_processor.channel = mock_channel
        event_processor.connection = mock_connection
        
        # Mock the logger
        with patch('app.services.event_processor.logger') as mock_logger:
            # Call the method
            asyncio.run(event_processor.close())
            
            # Verify methods were called
            mock_channel.close.assert_called_once()
            mock_connection.close.assert_called_once()
            
            # Verify logging
            mock_logger.info.assert_called()
            assert "RabbitMQ connection closed" in str(mock_logger.info.call_args)