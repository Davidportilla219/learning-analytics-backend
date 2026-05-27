"""
Event ingestion endpoints for the Event Capture Service.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime
import logging
import uuid

from app.database import get_db_session
from app.models.event import (
    Event, EventCreate, EventUpdate, EventResponse, 
    EventBatch, EventBatchResponse, EventStats
)
from app.services.event_processor import EventProcessor
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize event processor
event_processor = EventProcessor()


@router.post("/events", response_model=EventResponse, status_code=201)
async def create_event(
    event: EventCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db_session)
):
    """Create a single event."""
    try:
        # Check if event already exists
        result = await db.execute(
            select(Event).where(Event.event_id == event.event_id)
        )
        existing_event = result.scalar_one_or_none()
        
        if existing_event:
            raise HTTPException(
                status_code=409,
                detail=f"Event with ID {event.event_id} already exists"
            )
        
        # Create new event
        db_event = Event(
            event_id=event.event_id,
            event_type=event.event_type,
            user_id=event.user_id,
            session_id=event.session_id,
            course_id=event.course_id,
            timestamp=event.timestamp,
            data=event.data,
            event_metadata=event.event_metadata
        )
        
        db.add(db_event)
        await db.commit()
        await db.refresh(db_event)
        
        # Add background task for event processing
        background_tasks.add_task(
            event_processor.process_event,
            db_event
        )
        
        logger.info(f"Created event: {event.event_id}")
        
        return EventResponse.from_orm(db_event)
        
    except Exception as e:
        logger.error(f"Error creating event: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/events/batch", response_model=EventBatchResponse, status_code=201)
async def create_events_batch(
    batch: EventBatch,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db_session)
):
    """Create multiple events in batch."""
    created_count = 0
    failed_events = []
    errors = []
    
    for event_data in batch.events:
        try:
            # Check if event already exists
            result = await db.execute(
                select(Event).where(Event.event_id == event_data.event_id)
            )
            existing_event = result.scalar_one_or_none()
            
            if existing_event:
                failed_events.append({
                    "event_id": event_data.event_id,
                    "error": "Event already exists"
                })
                errors.append(f"Event {event_data.event_id} already exists")
                continue
            
            # Create new event
            db_event = Event(
                event_id=event_data.event_id,
                event_type=event_data.event_type,
                user_id=event_data.user_id,
                session_id=event_data.session_id,
                course_id=event_data.course_id,
                timestamp=event_data.timestamp,
                data=event_data.data,
                event_metadata=event_data.event_metadata
            )
            
            db.add(db_event)
            created_count += 1
            
            # Add background task for event processing
            background_tasks.add_task(
                event_processor.process_event,
                db_event
            )
            
        except Exception as e:
            logger.error(f"Error creating event {event_data.event_id}: {e}")
            failed_events.append({
                "event_id": event_data.event_id,
                "error": str(e)
            })
            errors.append(f"Error creating event {event_data.event_id}: {e}")
    
    # Commit all created events
    try:
        await db.commit()
        logger.info(f"Created {created_count} events in batch")
    except Exception as e:
        logger.error(f"Error committing batch: {e}")
        await db.rollback()
        errors.append(f"Error committing batch: {e}")
    
    return EventBatchResponse(
        created_count=created_count,
        failed_events=failed_events,
        errors=errors
    )


@router.get("/events/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Get a specific event by ID."""
    try:
        result = await db.execute(
            select(Event).where(Event.event_id == event_id)
        )
        event = result.scalar_one_or_none()
        
        if not event:
            raise HTTPException(
                status_code=404,
                detail=f"Event with ID {event_id} not found"
            )
        
        return EventResponse.from_orm(event)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting event {event_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/events", response_model=List[EventResponse])
async def get_events(
    user_id: Optional[str] = None,
    event_type: Optional[str] = None,
    course_id: Optional[str] = None,
    session_id: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db_session)
):
    """Get events with optional filtering."""
    try:
        # Build query
        query = select(Event)
        
        if user_id:
            query = query.where(Event.user_id == user_id)
        if event_type:
            query = query.where(Event.event_type == event_type)
        if course_id:
            query = query.where(Event.course_id == course_id)
        if session_id:
            query = query.where(Event.session_id == session_id)
        if start_time:
            query = query.where(Event.timestamp >= start_time)
        if end_time:
            query = query.where(Event.timestamp <= end_time)
        
        # Add pagination
        query = query.offset(offset).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        events = result.scalars().all()
        
        return [EventResponse.from_orm(event) for event in events]
        
    except Exception as e:
        logger.error(f"Error getting events: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/events/stats", response_model=EventStats)
async def get_event_stats(
    user_id: Optional[str] = None,
    course_id: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db_session)
):
    """Get event statistics."""
    try:
        # Build query for total events
        query = select(Event)
        
        if user_id:
            query = query.where(Event.user_id == user_id)
        if course_id:
            query = query.where(Event.course_id == course_id)
        if start_time:
            query = query.where(Event.timestamp >= start_time)
        if end_time:
            query = query.where(Event.timestamp <= end_time)
        
        # Get total events
        result = await db.execute(query)
        total_events = len(result.scalars().all())
        
        # Get unique users
        query = select(Event.user_id.distinct())
        if user_id:
            query = query.where(Event.user_id == user_id)
        if course_id:
            query = query.where(Event.course_id == course_id)
        if start_time:
            query = query.where(Event.timestamp >= start_time)
        if end_time:
            query = query.where(Event.timestamp <= end_time)
        
        result = await db.execute(query)
        unique_users = len(result.scalars().all())
        
        # Get event types
        event_types_query = select(Event.event_type, select(func.count(Event.id)).label('count'))
        if user_id:
            event_types_query = event_types_query.where(Event.user_id == user_id)
        if course_id:
            event_types_query = event_types_query.where(Event.course_id == course_id)
        if start_time:
            event_types_query = event_types_query.where(Event.timestamp >= start_time)
        if end_time:
            event_types_query = event_types_query.where(Event.timestamp <= end_time)
        
        event_types_query = event_types_query.group_by(Event.event_type)
        result = await db.execute(event_types_query)
        event_types = {row.event_type: row.count for row in result}
        
        # Get time range
        time_query = select(Event.timestamp)
        if user_id:
            time_query = time_query.where(Event.user_id == user_id)
        if course_id:
            time_query = time_query.where(Event.course_id == course_id)
        if start_time:
            time_query = time_query.where(Event.timestamp >= start_time)
        if end_time:
            time_query = time_query.where(Event.timestamp <= end_time)
        
        result = await db.execute(time_query.order_by(Event.timestamp))
        timestamps = [row.timestamp for row in result]
        
        time_range = {
            "start": min(timestamps) if timestamps else None,
            "end": max(timestamps) if timestamps else None
        }
        
        # Calculate average events per user
        avg_events_per_user = total_events / unique_users if unique_users > 0 else 0
        
        return EventStats(
            total_events=total_events,
            unique_users=unique_users,
            event_types=event_types,
            time_range=time_range,
            avg_events_per_user=avg_events_per_user
        )
        
    except Exception as e:
        logger.error(f"Error getting event stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/events/{event_id}", status_code=204)
async def delete_event(
    event_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Delete an event."""
    try:
        result = await db.execute(
            select(Event).where(Event.event_id == event_id)
        )
        event = result.scalar_one_or_none()
        
        if not event:
            raise HTTPException(
                status_code=404,
                detail=f"Event with ID {event_id} not found"
            )
        
        await db.delete(event)
        await db.commit()
        
        logger.info(f"Deleted event: {event_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting event {event_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/events/health")
async def events_health():
    """Health check for events endpoint."""
    return {"status": "healthy", "message": "Events endpoint is healthy"}