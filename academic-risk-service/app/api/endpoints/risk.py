"""
Risk assessment endpoints for the Academic Risk Service.
"""

import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional, Dict, Any
import json

from app.database import get_db_session
from app.models.health import RiskAssessment, UserRiskProfile, RiskAlert
from app.services.risk_assessor import RiskAssessor
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize risk assessor
risk_assessor = RiskAssessor()


@router.post("/risk/assess", response_model=RiskAssessment, status_code=201)
async def assess_user_risk(
    user_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db_session)
):
    """Assess academic risk for a specific user."""
    try:
        # Get user's recent events
        query = select(func.jsonb_build_object(
            'user_id', user_id,
            'assessment_timestamp', datetime.now().isoformat(),
            'risk_factors', await risk_assessor.analyze_user_events(user_id, db),
            'risk_score', 0.0,  # Placeholder, will be calculated
            'risk_level', 'low'   # Placeholder, will be calculated
        ))
        
        # Assess risk
        risk_assessment = await risk_assessor.assess_academic_risk(user_id, db)
        
        # Store risk assessment
        db_risk = RiskAssessment(
            user_id=user_id,
            risk_score=risk_assessment["risk_score"],
            risk_level=risk_assessment["risk_level"],
            risk_factors=risk_assessment["risk_factors"],
            recommendations=risk_assessment["recommendations"],
            assessment_timestamp=datetime.now(),
            course_id=risk_assessment.get("course_id")
        )
        
        # Add background task for alert generation
        if risk_assessment["risk_level"] in ["high", "critical"]:
            background_tasks.add_task(
                risk_assessor.generate_risk_alert,
                risk_assessment,
                db
            )
        
        logger.info(f"Assessed risk for user: {user_id}")
        
        return db_risk
        
    except Exception as e:
        logger.error(f"Error assessing risk for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/risk/profile/{user_id}", response_model=UserRiskProfile)
async def get_user_risk_profile(
    user_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Get user's comprehensive risk profile."""
    try:
        # Get user's risk history
        query = select(func.jsonb_build_object(
            'user_id', user_id,
            'overall_risk_score', 0.0,  # Placeholder
            'overall_risk_level', 'low',  # Placeholder
            'risk_history', [],  # Placeholder
            'last_assessment', datetime.now(),
            'courses_at_risk', [],  # Placeholder
            'intervention_needed', False  # Placeholder
        ))
        
        risk_profile = await risk_assessor.get_user_risk_profile(user_id, db)
        
        return UserRiskProfile(
            user_id=user_id,
            overall_risk_score=risk_profile["overall_risk_score"],
            overall_risk_level=risk_profile["overall_risk_level"],
            risk_history=risk_profile["risk_history"],
            last_assessment=risk_profile["last_assessment"],
            courses_at_risk=risk_profile["courses_at_risk"],
            intervention_needed=risk_profile["intervention_needed"]
        )
        
    except Exception as e:
        logger.error(f"Error getting risk profile for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/risk/users", response_model=List[UserRiskProfile])
async def get_users_at_risk(
    risk_level: Optional[str] = None,
    course_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db_session)
):
    """Get users at risk with optional filtering."""
    try:
        users_at_risk = await risk_assessor.get_users_at_risk(
            risk_level=risk_level,
            course_id=course_id,
            limit=limit,
            offset=offset,
            db=db
        )
        
        return [UserRiskProfile(
            user_id=user["user_id"],
            overall_risk_score=user["overall_risk_score"],
            overall_risk_level=user["overall_risk_level"],
            risk_history=user["risk_history"],
            last_assessment=user["last_assessment"],
            courses_at_risk=user["courses_at_risk"],
            intervention_needed=user["intervention_needed"]
        ) for user in users_at_risk]
        
    except Exception as e:
        logger.error(f"Error getting users at risk: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/risk/alerts", response_model=List[RiskAlert])
async def get_risk_alerts(
    user_id: Optional[str] = None,
    risk_level: Optional[str] = None,
    course_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db_session)
):
    """Get risk alerts with optional filtering."""
    try:
        alerts = await risk_assessor.get_risk_alerts(
            user_id=user_id,
            risk_level=risk_level,
            course_id=course_id,
            limit=limit,
            offset=offset,
            db=db
        )
        
        return [RiskAlert(
            alert_id=alert["alert_id"],
            user_id=alert["user_id"],
            risk_score=alert["risk_score"],
            risk_level=alert["risk_level"],
            alert_type=alert["alert_type"],
            message=alert["message"],
            timestamp=alert["timestamp"],
            course_id=alert.get("course_id"),
            instructor_id=alert.get("instructor_id"),
            acknowledged=alert.get("acknowledged", False),
            resolved=alert.get("resolved", False)
        ) for alert in alerts]
        
    except Exception as e:
        logger.error(f"Error getting risk alerts: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/risk/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Acknowledge a risk alert."""
    try:
        await risk_assessor.acknowledge_alert(alert_id, db)
        return {"message": "Alert acknowledged successfully"}
        
    except Exception as e:
        logger.error(f"Error acknowledging alert {alert_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/risk/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Resolve a risk alert."""
    try:
        await risk_assessor.resolve_alert(alert_id, db)
        return {"message": "Alert resolved successfully"}
        
    except Exception as e:
        logger.error(f"Error resolving alert {alert_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/risk/stats")
async def get_risk_statistics(
    course_id: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db_session)
):
    """Get risk statistics."""
    try:
        stats = await risk_assessor.get_risk_statistics(
            course_id=course_id,
            start_time=start_time,
            end_time=end_time,
            db=db
        )
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting risk statistics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/risk/health")
async def risk_health():
    """Health check for risk endpoints."""
    return {"status": "healthy", "message": "Risk assessment endpoints are healthy"}