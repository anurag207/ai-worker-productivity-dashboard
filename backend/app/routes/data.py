"""
Data management API routes.

Provides endpoints for:
- Seeding sample data (workers, workstations)
- Generating dummy events
- Refreshing data for testing

These endpoints allow evaluators to add or refresh data
without manually editing the database or frontend code.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import SeedDataResult, RefreshDataRequest
from ..services.data_generator import (
    seed_sample_data,
    generate_dummy_events,
    clear_all_events
)

router = APIRouter(prefix="/data", tags=["data management"])


@router.post("/seed", response_model=SeedDataResult)
def seed_data(db: Session = Depends(get_db)):
    """
    Seed the database with sample workers and workstations.
    
    Creates:
    - 6 sample workers (W1-W6)
    - 6 sample workstations (S1-S6)
    
    Skips entries that already exist (idempotent).
    """
    workers_created, stations_created = seed_sample_data(db)
    
    return SeedDataResult(
        workers_created=workers_created,
        workstations_created=stations_created,
        events_generated=0,
        message=f"Seeded {workers_created} workers and {stations_created} workstations"
    )


@router.post("/generate-events", response_model=SeedDataResult)
def generate_events(
    request: RefreshDataRequest = RefreshDataRequest(),
    db: Session = Depends(get_db)
):
    """
    Generate dummy event data for testing.
    
    Parameters:
    - clear_existing: If true, deletes all existing events first
    - num_days: Number of days of data to generate (1-30)
    - events_per_day: Approximate events per day (10-1000)
    
    The generator creates realistic patterns:
    - Work shifts (8 AM - 4 PM)
    - Higher working probability during core hours
    - Production events correlated with working time
    """
    try:
        events_count = generate_dummy_events(
            db,
            num_days=request.num_days,
            events_per_day=request.events_per_day,
            clear_existing=request.clear_existing
        )
        
        return SeedDataResult(
            workers_created=0,
            workstations_created=0,
            events_generated=events_count,
            message=f"Generated {events_count} events over {request.num_days} days"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/initialize", response_model=SeedDataResult)
def initialize_data(db: Session = Depends(get_db)):
    """
    Initialize database with sample data and dummy events.
    
    Convenience endpoint that:
    1. Seeds workers and workstations
    2. Generates 7 days of dummy event data
    
    Perfect for first-time setup or demos.
    """
    workers_created, stations_created = seed_sample_data(db)
    events_count = generate_dummy_events(db, num_days=7, events_per_day=100)
    
    return SeedDataResult(
        workers_created=workers_created,
        workstations_created=stations_created,
        events_generated=events_count,
        message="Database initialized with sample data"
    )


@router.delete("/events")
def clear_events(db: Session = Depends(get_db)):
    """
    Delete all events from the database.
    
    Workers and workstations are preserved.
    Useful for resetting to a clean state before generating new data.
    """
    count = clear_all_events(db)
    return {"deleted": count, "message": f"Deleted {count} events"}


@router.post("/refresh", response_model=SeedDataResult)
def refresh_data(
    request: RefreshDataRequest = RefreshDataRequest(clear_existing=True, num_days=7, events_per_day=100),
    db: Session = Depends(get_db)
):
    """
    Refresh all data - clears existing and generates new.
    
    This is the main endpoint for evaluators to refresh data.
    Always clears existing events and generates fresh data.
    """
    # Ensure workers and workstations exist
    workers_created, stations_created = seed_sample_data(db)
    
    # Generate fresh events
    events_count = generate_dummy_events(
        db,
        num_days=request.num_days,
        events_per_day=request.events_per_day,
        clear_existing=True  # Always clear for refresh
    )
    
    return SeedDataResult(
        workers_created=workers_created,
        workstations_created=stations_created,
        events_generated=events_count,
        message=f"Data refreshed: {events_count} new events generated"
    )




