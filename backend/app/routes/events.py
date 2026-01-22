"""
Event ingestion API routes.

Handles receiving AI-generated events from CCTV systems.

=== HANDLING EDGE CASES ===

1. Intermittent Connectivity:
   - Events can be buffered on edge devices and sent in batches
   - We accept batch submissions via POST /events/batch
   - Events are processed idempotently (duplicates are skipped)

2. Duplicate Events:
   - Database has unique constraint on (timestamp, worker_id, workstation_id, event_type)
   - Exact duplicates are silently skipped
   - Response includes count of duplicates for monitoring

3. Out-of-Order Timestamps:
   - Events are stored with their original timestamps
   - We also record 'received_at' for ordering by arrival time
   - Metrics queries can use either timestamp for different use cases
"""
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..database import get_db
from ..models import Event, Worker, Workstation
from ..schemas import EventCreate, EventResponse, EventBatchCreate, EventIngestionResult
from ..config import DUPLICATE_DETECTION_WINDOW_SECONDS

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/", response_model=EventResponse, status_code=201)
def ingest_event(event: EventCreate, db: Session = Depends(get_db)):
    """
    Ingest a single AI event from CCTV system.
    
    This endpoint handles:
    - Validation of event data
    - Duplicate detection and rejection
    - Storage of valid events
    
    Returns:
        The created event with its database ID
        
    Raises:
        400: If worker or workstation doesn't exist
        409: If duplicate event detected
    """
    # Validate worker exists
    worker = db.query(Worker).filter(Worker.worker_id == event.worker_id).first()
    if not worker:
        raise HTTPException(status_code=400, detail=f"Worker '{event.worker_id}' not found")
    
    # Validate workstation exists
    workstation = db.query(Workstation).filter(Workstation.station_id == event.workstation_id).first()
    if not workstation:
        raise HTTPException(status_code=400, detail=f"Workstation '{event.workstation_id}' not found")
    
    # Create event
    db_event = Event(
        timestamp=event.timestamp,
        worker_id=event.worker_id,
        workstation_id=event.workstation_id,
        event_type=event.event_type,
        confidence=event.confidence,
        count=event.count or 0,
        received_at=datetime.utcnow()
    )
    
    try:
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        return db_event
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Duplicate event detected (same timestamp, worker, workstation, event_type)"
        )


@router.post("/batch", response_model=EventIngestionResult)
def ingest_events_batch(batch: EventBatchCreate, db: Session = Depends(get_db)):
    """
    Ingest multiple events in a single request.
    
    Ideal for:
    - Edge devices with intermittent connectivity
    - Batch uploads of buffered events
    - High-throughput event streams
    
    Processing:
    - Events are processed individually
    - Duplicates are skipped (not errors)
    - Invalid events are logged but don't fail the batch
    - Returns summary of results
    """
    total = len(batch.events)
    stored = 0
    duplicates = 0
    errors = []
    
    # Get valid worker and workstation IDs
    valid_workers = {w.worker_id for w in db.query(Worker).all()}
    valid_stations = {s.station_id for s in db.query(Workstation).all()}
    
    for event in batch.events:
        # Validate references
        if event.worker_id not in valid_workers:
            errors.append(f"Unknown worker_id: {event.worker_id}")
            continue
        if event.workstation_id not in valid_stations:
            errors.append(f"Unknown workstation_id: {event.workstation_id}")
            continue
        
        # Create event
        db_event = Event(
            timestamp=event.timestamp,
            worker_id=event.worker_id,
            workstation_id=event.workstation_id,
            event_type=event.event_type,
            confidence=event.confidence,
            count=event.count or 0,
            received_at=datetime.utcnow()
        )
        
        try:
            db.add(db_event)
            db.flush()
            stored += 1
        except IntegrityError:
            db.rollback()
            duplicates += 1
    
    db.commit()
    
    return EventIngestionResult(
        total_received=total,
        successfully_stored=stored,
        duplicates_skipped=duplicates,
        errors=errors[:10]  # Limit errors in response
    )


@router.get("/", response_model=List[EventResponse])
def list_events(
    worker_id: Optional[str] = Query(None, description="Filter by worker ID"),
    workstation_id: Optional[str] = Query(None, description="Filter by workstation ID"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    start_time: Optional[datetime] = Query(None, description="Filter events after this time"),
    end_time: Optional[datetime] = Query(None, description="Filter events before this time"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum events to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db)
):
    """
    List events with optional filters.
    
    Supports filtering by:
    - Worker
    - Workstation
    - Event type
    - Time range
    
    Results are ordered by timestamp (newest first) by default.
    """
    query = db.query(Event)
    
    if worker_id:
        query = query.filter(Event.worker_id == worker_id)
    if workstation_id:
        query = query.filter(Event.workstation_id == workstation_id)
    if event_type:
        query = query.filter(Event.event_type == event_type)
    if start_time:
        query = query.filter(Event.timestamp >= start_time)
    if end_time:
        query = query.filter(Event.timestamp <= end_time)
    
    events = query.order_by(Event.timestamp.desc()).offset(offset).limit(limit).all()
    return events


@router.get("/count")
def count_events(
    worker_id: Optional[str] = Query(None),
    workstation_id: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    """Get count of events matching filters."""
    query = db.query(Event)
    
    if worker_id:
        query = query.filter(Event.worker_id == worker_id)
    if workstation_id:
        query = query.filter(Event.workstation_id == workstation_id)
    if event_type:
        query = query.filter(Event.event_type == event_type)
    if start_time:
        query = query.filter(Event.timestamp >= start_time)
    if end_time:
        query = query.filter(Event.timestamp <= end_time)
    
    return {"count": query.count()}




