"""
Event processing service with normalization and risk assessment.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import statistics

from app.core.config import settings

logger = logging.getLogger(__name__)


class EventProcessor:
    """Service for processing and normalizing events."""
    
    def __init__(self):
        self.event_type_mappings = {
            # Authentication events
            'login': 'authentication_login',
            'logout': 'authentication_logout',
            
            # Content interaction events
            'page_view': 'content_page_view',
            'video_play': 'content_video_play',
            'video_pause': 'content_video_pause',
            'resource_download': 'content_download',
            
            # Assignment events
            'assignment_view': 'assignment_view',
            'assignment_submit': 'assignment_submit',
            
            # Quiz events
            'quiz_start': 'quiz_start',
            'quiz_submit': 'quiz_submit',
            
            # Forum events
            'forum_post': 'forum_post',
            'forum_reply': 'forum_reply',
            
            # Navigation events
            'search': 'navigation_search',
            'navigation': 'navigation_general',
            'assessment': 'assessment_taken',
            'completion': 'course_completion'
        }
        
        self.risk_factors = {
            'login': 0.1,
            'logout': 0.0,
            'page_view': 0.05,
            'video_play': 0.1,
            'video_pause': 0.02,
            'resource_download': 0.1,
            'assignment_view': 0.15,
            'assignment_submit': 0.2,
            'quiz_start': 0.1,
            'quiz_submit': 0.25,
            'forum_post': 0.2,
            'forum_reply': 0.15,
            'search': 0.1,
            'navigation': 0.05,
            'assessment': 0.3,
            'completion': 0.1
        }
    
    async def process_raw_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and normalize a raw event."""
        start_time = datetime.now()
        
        try:
            # Extract basic event information
            event_id = event_data.get("event_id")
            original_event_type = event_data.get("event_type")
            user_id = event_data.get("user_id")
            timestamp = event_data.get("timestamp")
            data = event_data.get("data", {})
            
            # Map event type to normalized type
            processed_event_type = self.event_type_mappings.get(
                original_event_type, 
                f"unknown_{original_event_type}"
            )
            
            # Calculate risk score
            risk_score = self._calculate_risk_score(original_event_type, data)
            risk_level = self._get_risk_level(risk_score)
            
            # Process event data
            processed_data = self._process_event_data(original_event_type, data)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "event_id": event_id,
                "original_event_type": original_event_type,
                "processed_event_type": processed_event_type,
                "user_id": user_id,
                "course_id": data.get("course_id"),
                "timestamp": timestamp,
                "processed_data": processed_data,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "processing_time": processing_time
            }
            
        except Exception as e:
            logger.error(f"Error processing event {event_data.get('event_id', 'unknown')}: {e}")
            raise
    
    def _calculate_risk_score(self, event_type: str, event_data: Dict[str, Any]) -> float:
        """Calculate risk score based on event type and data."""
        base_score = self.risk_factors.get(event_type, 0.0)
        
        # Adjust score based on event data
        if event_type == "login":
            # Multiple login attempts increase risk
            ip_address = event_data.get("ip_address")
            if ip_address:
                # TODO: Check for suspicious IP patterns
                pass
        
        elif event_type == "assignment_submit":
            # Late submissions increase risk
            due_date = event_data.get("due_date")
            if due_date:
                submission_time = datetime.fromisoformat(event_data.get("timestamp"))
                due_datetime = datetime.fromisoformat(due_date)
                if submission_time > due_datetime:
                    base_score += 0.2
        
        elif event_type == "quiz_submit":
            # Low scores increase risk
            score = event_data.get("score")
            if score is not None:
                base_score += (1.0 - score) * 0.3
        
        elif event_type == "forum_post":
            # Negative sentiment in posts increases risk
            # TODO: Implement sentiment analysis
            pass
        
        return min(base_score, 1.0)  # Cap at 1.0
    
    def _get_risk_level(self, risk_score: float) -> str:
        """Get risk level based on score."""
        if risk_score < settings.RISK_THRESHOLD_LOW:
            return "low"
        elif risk_score < settings.RISK_THRESHOLD_MEDIUM:
            return "medium"
        elif risk_score < settings.RISK_THRESHOLD_HIGH:
            return "high"
        else:
            return "critical"
    
    def _process_event_data(self, event_type: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process event data based on event type."""
        processed = {
            "original_data": event_data,
            "processed_at": datetime.now().isoformat(),
            "event_category": self._get_event_category(event_type)
        }
        
        # Add type-specific processing
        if event_type == "login":
            processed.update({
                "login_method": event_data.get("user_agent", "unknown"),
                "location": event_data.get("ip_address", "unknown")
            })
        
        elif event_type == "video_play":
            processed.update({
                "video_duration": event_data.get("duration", 0),
                "video_quality": event_data.get("quality", "unknown")
            })
        
        elif event_type == "assignment_submit":
            processed.update({
                "assignment_id": event_data.get("assignment_id"),
                "submission_time": event_data.get("timestamp"),
                "lateness": self._calculate_lateness(event_data)
            })
        
        elif event_type == "quiz_submit":
            processed.update({
                "quiz_id": event_data.get("quiz_id"),
                "score": event_data.get("score"),
                "max_score": event_data.get("max_score", 100),
                "time_spent": event_data.get("time_spent", 0)
            })
        
        return processed
    
    def _get_event_category(self, event_type: str) -> str:
        """Get event category based on event type."""
        category_mapping = {
            'login': 'authentication',
            'logout': 'authentication',
            'page_view': 'content',
            'video_play': 'content',
            'video_pause': 'content',
            'resource_download': 'content',
            'assignment_view': 'assignment',
            'assignment_submit': 'assignment',
            'quiz_start': 'assessment',
            'quiz_submit': 'assessment',
            'forum_post': 'social',
            'forum_reply': 'social',
            'search': 'navigation',
            'navigation': 'navigation',
            'assessment': 'assessment',
            'completion': 'achievement'
        }
        return category_mapping.get(event_type, 'other')
    
    def _calculate_lateness(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate assignment lateness."""
        try:
            submission_time = datetime.fromisoformat(event_data.get("timestamp"))
            due_date = datetime.fromisoformat(event_data.get("due_date"))
            
            lateness = submission_time - due_date
            days_late = lateness.total_seconds() / (24 * 3600)
            
            return {
                "days_late": max(0, days_late),
                "hours_late": max(0, lateness.total_seconds() / 3600),
                "is_late": days_late > 0
            }
        except Exception:
            return {"days_late": 0, "hours_late": 0, "is_late": False}
    
    async def assess_risk(self, processed_event: Dict[str, Any], db_session):
        """Assess risk and potentially trigger alerts."""
        try:
            risk_score = processed_event.get("risk_score")
            risk_level = processed_event.get("risk_level")
            
            if risk_level in ["high", "critical"]:
                # TODO: Store risk assessment and trigger alerts
                logger.warning(
                    f"High risk event detected: {processed_event['event_id']} "
                    f"Risk level: {risk_level}, Score: {risk_score}"
                )
                
                # TODO: Send to alert service
                # await self._send_alert(processed_event)
            
        except Exception as e:
            logger.error(f"Error assessing risk for event {processed_event.get('event_id')}: {e}")
    
    async def _send_alert(self, processed_event: Dict[str, Any]):
        """Send alert to alert service."""
        # TODO: Implement alert sending via RabbitMQ or HTTP
        pass
    
    async def get_processing_stats(self, db_session) -> Dict[str, Any]:
        """Get processing statistics."""
        # TODO: Implement statistics calculation from database
        return {
            "total_processed": 0,
            "success_rate": 1.0,
            "average_processing_time": 0.1,
            "error_count": 0,
            "risk_distribution": {"low": 0, "medium": 0, "high": 0, "critical": 0}
        }