"""
Risk assessment service for the Academic Risk Service.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

import json

from app.models.health import RiskAssessment, UserRiskProfile, RiskAlert
from app.core.config import settings

logger = logging.getLogger(__name__)


class RiskAssessor:
    """Risk assessment service for academic risk prediction."""
    
    def __init__(self):
        self.risk_thresholds = {
            "low": settings.RISK_THRESHOLD_LOW,
            "medium": settings.RISK_THRESHOLD_MEDIUM,
            "high": settings.RISK_THRESHOLD_HIGH
        }
    
    async def assess_academic_risk(self, user_id: str, db: AsyncSession) -> Dict[str, Any]:
        """Assess academic risk for a specific user."""
        try:
            # Get user's recent events (last 30 days)
            events = await self.get_user_events(user_id, db)
            
            # Analyze risk factors
            risk_factors = await self.analyze_user_events(user_id, db)
            
            # Calculate risk score
            risk_score = self.calculate_risk_score(risk_factors)
            
            # Determine risk level
            risk_level = self.determine_risk_level(risk_score)
            
            # Generate recommendations
            recommendations = self.generate_recommendations(risk_factors, risk_level)
            
            # Get course information
            courses_at_risk = await self.get_courses_at_risk(user_id, db)
            
            return {
                "user_id": user_id,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "risk_factors": risk_factors,
                "recommendations": recommendations,
                "courses_at_risk": courses_at_risk,
                "assessment_timestamp": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error assessing risk for user {user_id}: {e}")
            raise
    
    async def get_user_events(self, user_id: str, db: AsyncSession) -> List[Dict[str, Any]]:
        """Get user's recent events from the event database."""
        try:
            # This would query the event database
            # For now, return placeholder data
            return [
                {
                    "event_type": "login",
                    "timestamp": datetime.now() - timedelta(days=1),
                    "metadata": {"device": "mobile"}
                },
                {
                    "event_type": "assignment_submit",
                    "timestamp": datetime.now() - timedelta(days=2),
                    "metadata": {"assignment_id": "assignment_1", "score": 75}
                }
            ]
        except Exception as e:
            logger.error(f"Error getting user events for {user_id}: {e}")
            return []
    
    async def analyze_user_events(self, user_id: str, db: AsyncSession) -> List[Dict[str, Any]]:
        """Analyze user events to identify risk factors."""
        try:
            events = await self.get_user_events(user_id, db)
            risk_factors = []
            
            # Analyze login patterns
            login_events = [e for e in events if e["event_type"] == "login"]
            if len(login_events) < settings.MIN_LOGIN_THRESHOLD:
                risk_factors.append({
                    "factor": "low_login_frequency",
                    "severity": "medium",
                    "description": "User has low login frequency"
                })
            
            # Analyze assignment submission patterns
            assignment_events = [e for e in events if e["event_type"] == "assignment_submit"]
            if len(assignment_events) < settings.MIN_ASSIGNMENT_THRESHOLD:
                risk_factors.append({
                    "factor": "low_assignment_frequency",
                    "severity": "high",
                    "description": "User has low assignment submission frequency"
                })
            
            # Analyze forum participation
            forum_events = [e for e in events if e["event_type"] == "forum_post"]
            if len(forum_events) < settings.MIN_FORUM_THRESHOLD:
                risk_factors.append({
                    "factor": "low_forum_participation",
                    "severity": "medium",
                    "description": "User has low forum participation"
                })
            
            # Analyze video consumption
            video_events = [e for e in events if e["event_type"] == "video_watch"]
            if len(video_events) < settings.MIN_VIDEO_THRESHOLD:
                risk_factors.append({
                    "factor": "low_video_consumption",
                    "severity": "low",
                    "description": "User has low video consumption"
                })
            
            # Analyze assessment performance
            assessment_events = [e for e in events if e["event_type"] == "assessment_complete"]
            if len(assessment_events) < settings.MIN_ASSESSMENT_THRESHOLD:
                risk_factors.append({
                    "factor": "low_assessment_frequency",
                    "severity": "medium",
                    "description": "User has low assessment completion frequency"
                })
            
            # Analyze recent performance trends
            recent_performance = self.analyze_recent_performance(events)
            if recent_performance["trend"] == "declining":
                risk_factors.append({
                    "factor": "declining_performance",
                    "severity": "high",
                    "description": "User shows declining performance trends"
                })
            
            return risk_factors
            
        except Exception as e:
            logger.error(f"Error analyzing user events for {user_id}: {e}")
            return []
    
    def analyze_recent_performance(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze recent performance trends."""
        try:
            # This is a simplified analysis
            # In a real implementation, you would analyze actual performance metrics
            return {
                "trend": "stable",  # Placeholder
                "recent_score": 75,  # Placeholder
                "previous_score": 80,  # Placeholder
                "change": -5  # Placeholder
            }
        except Exception as e:
            logger.error(f"Error analyzing performance trends: {e}")
            return {"trend": "unknown"}
    
    def calculate_risk_score(self, risk_factors: List[Dict[str, Any]]) -> float:
        """Calculate risk score based on risk factors."""
        try:
            if not risk_factors:
                return 0.0
            
            base_score = 0.0
            for factor in risk_factors:
                if factor["severity"] == "low":
                    base_score += 0.2
                elif factor["severity"] == "medium":
                    base_score += 0.4
                elif factor["severity"] == "high":
                    base_score += 0.6
            
            # Normalize to 0-1 range
            return min(base_score / len(risk_factors), 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating risk score: {e}")
            return 0.0
    
    def determine_risk_level(self, risk_score: float) -> str:
        """Determine risk level based on score."""
        if risk_score < self.risk_thresholds["low"]:
            return "low"
        elif risk_score < self.risk_thresholds["medium"]:
            return "medium"
        elif risk_score < self.risk_thresholds["high"]:
            return "high"
        else:
            return "critical"
    
    def generate_recommendations(self, risk_factors: List[Dict[str, Any]], risk_level: str) -> List[str]:
        """Generate recommendations based on risk factors."""
        recommendations = []
        
        if risk_level == "critical":
            recommendations.extend([
                "Immediate intervention required",
                "Schedule urgent meeting with instructor",
                "Consider academic support services"
            ])
        elif risk_level == "high":
            recommendations.extend([
                "Schedule meeting with instructor",
                "Review course materials",
                "Increase study time"
            ])
        elif risk_level == "medium":
            recommendations.extend([
                "Monitor progress closely",
                "Review course materials",
                "Participate in discussions"
            ])
        
        # Add specific recommendations based on risk factors
        for factor in risk_factors:
            if factor["factor"] == "low_login_frequency":
                recommendations.append("Increase login frequency")
            elif factor["factor"] == "low_assignment_frequency":
                recommendations.append("Complete more assignments")
            elif factor["factor"] == "low_forum_participation":
                recommendations.append("Participate in forum discussions")
            elif factor["factor"] == "low_video_consumption":
                recommendations.append("Watch course videos")
            elif factor["factor"] == "low_assessment_frequency":
                recommendations.append("Complete more assessments")
            elif factor["factor"] == "declining_performance":
                recommendations.append("Review study strategies")
        
        return list(set(recommendations))  # Remove duplicates
    
    async def get_user_risk_profile(self, user_id: str, db: AsyncSession) -> Dict[str, Any]:
        """Get user's comprehensive risk profile."""
        try:
            # Get recent risk assessments
            recent_assessments = await self.get_recent_assessments(user_id, db)
            
            if not recent_assessments:
                # No recent assessments, return default profile
                return {
                    "user_id": user_id,
                    "overall_risk_score": 0.0,
                    "overall_risk_level": "low",
                    "risk_history": [],
                    "last_assessment": datetime.now(),
                    "courses_at_risk": [],
                    "intervention_needed": False
                }
            
            # Calculate overall risk score
            overall_score = sum(a["risk_score"] for a in recent_assessments) / len(recent_assessments)
            overall_level = self.determine_risk_level(overall_score)
            
            # Get courses at risk
            courses_at_risk = await self.get_courses_at_risk(user_id, db)
            
            # Determine if intervention is needed
            intervention_needed = overall_level in ["high", "critical"]
            
            return {
                "user_id": user_id,
                "overall_risk_score": overall_score,
                "overall_risk_level": overall_level,
                "risk_history": recent_assessments,
                "last_assessment": recent_assessments[-1]["assessment_timestamp"],
                "courses_at_risk": courses_at_risk,
                "intervention_needed": intervention_needed
            }
            
        except Exception as e:
            logger.error(f"Error getting user risk profile for {user_id}: {e}")
            raise
    
    async def get_recent_assessments(self, user_id: str, db: AsyncSession) -> List[Dict[str, Any]]:
        """Get recent risk assessments for a user."""
        try:
            # This would query the risk assessment database
            # For now, return placeholder data
            return [
                {
                    "user_id": user_id,
                    "risk_score": 0.4,
                    "risk_level": "medium",
                    "assessment_timestamp": datetime.now() - timedelta(days=7),
                    "risk_factors": [],
                    "recommendations": ["Monitor progress"]
                }
            ]
        except Exception as e:
            logger.error(f"Error getting recent assessments for {user_id}: {e}")
            return []
    
    async def get_users_at_risk(self, risk_level: Optional[str] = None, 
                              course_id: Optional[str] = None, 
                              limit: int = 100, 
                              offset: int = 0,
                              db: AsyncSession = None) -> List[Dict[str, Any]]:
        """Get users at risk with optional filtering."""
        try:
            # This would query the database for users at risk
            # For now, return placeholder data
            return [
                {
                    "user_id": "user_1",
                    "overall_risk_score": 0.7,
                    "overall_risk_level": "high",
                    "risk_history": [],
                    "last_assessment": datetime.now(),
                    "courses_at_risk": ["course_1"],
                    "intervention_needed": True
                }
            ]
        except Exception as e:
            logger.error(f"Error getting users at risk: {e}")
            return []
    
    async def get_risk_alerts(self, user_id: Optional[str] = None,
                            risk_level: Optional[str] = None,
                            course_id: Optional[str] = None,
                            limit: int = 100,
                            offset: int = 0,
                            db: AsyncSession = None) -> List[Dict[str, Any]]:
        """Get risk alerts with optional filtering."""
        try:
            # This would query the risk alert database
            # For now, return placeholder data
            return [
                {
                    "alert_id": "alert_1",
                    "user_id": "user_1",
                    "risk_score": 0.8,
                    "risk_level": "high",
                    "alert_type": "academic_risk",
                    "message": "User shows declining performance",
                    "timestamp": datetime.now(),
                    "course_id": "course_1",
                    "instructor_id": "instructor_1",
                    "acknowledged": False,
                    "resolved": False
                }
            ]
        except Exception as e:
            logger.error(f"Error getting risk alerts: {e}")
            return []
    
    async def get_courses_at_risk(self, user_id: str, db: AsyncSession) -> List[str]:
        """Get courses that a user is at risk in."""
        try:
            # This would analyze the user's performance across courses
            # For now, return placeholder data
            return ["course_1", "course_2"]
        except Exception as e:
            logger.error(f"Error getting courses at risk for {user_id}: {e}")
            return []
    
    async def generate_risk_alert(self, risk_assessment: Dict[str, Any], db: AsyncSession):
        """Generate risk alert for high-risk users."""
        try:
            if risk_assessment["risk_level"] in ["high", "critical"]:
                alert = RiskAlert(
                    alert_id=f"alert_{risk_assessment['user_id']}_{datetime.now().timestamp()}",
                    user_id=risk_assessment["user_id"],
                    risk_score=risk_assessment["risk_score"],
                    risk_level=risk_assessment["risk_level"],
                    alert_type="academic_risk",
                    message=f"User is at {risk_assessment['risk_level']} risk level",
                    timestamp=datetime.now(),
                    course_id=risk_assessment.get("course_id")
                )
                
                # Store alert in database
                # This would be implemented with proper database operations
                logger.info(f"Generated risk alert for user {risk_assessment['user_id']}")
                
        except Exception as e:
            logger.error(f"Error generating risk alert: {e}")
    
    async def acknowledge_alert(self, alert_id: str, db: AsyncSession):
        """Acknowledge a risk alert."""
        try:
            # This would update the alert in the database
            logger.info(f"Acknowledged alert {alert_id}")
        except Exception as e:
            logger.error(f"Error acknowledging alert {alert_id}: {e}")
            raise
    
    async def resolve_alert(self, alert_id: str, db: AsyncSession):
        """Resolve a risk alert."""
        try:
            # This would update the alert in the database
            logger.info(f"Resolved alert {alert_id}")
        except Exception as e:
            logger.error(f"Error resolving alert {alert_id}: {e}")
            raise
    
    async def get_risk_statistics(self, course_id: Optional[str] = None,
                                 start_time: Optional[datetime] = None,
                                 end_time: Optional[datetime] = None,
                                 db: AsyncSession = None) -> Dict[str, Any]:
        """Get risk statistics."""
        try:
            # This would query the database for risk statistics
            # For now, return placeholder data
            return {
                "total_users": 100,
                "users_at_risk": 25,
                "risk_distribution": {
                    "low": 60,
                    "medium": 15,
                    "high": 8,
                    "critical": 2
                },
                "alerts_generated": 10,
                "alerts_acknowledged": 8,
                "alerts_resolved": 5
            }
        except Exception as e:
            logger.error(f"Error getting risk statistics: {e}")
            raise