"""
Data generation service for seeding and testing.

This module provides functionality to:
1. Create sample workers and workstations
2. Generate realistic dummy event data
3. Refresh data without manual database editing
"""
import random
from datetime import datetime, timedelta
from typing import Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..models import Worker, Workstation, Event


# Sample worker data
SAMPLE_WORKERS = [
    {"worker_id": "W1", "name": "John Martinez"},
    {"worker_id": "W2", "name": "Sarah Chen"},
    {"worker_id": "W3", "name": "Michael Johnson"},
    {"worker_id": "W4", "name": "Emily Davis"},
    {"worker_id": "W5", "name": "Robert Kim"},
    {"worker_id": "W6", "name": "Lisa Thompson"},
]

# Sample workstation data
SAMPLE_WORKSTATIONS = [
    {"station_id": "S1", "name": "Assembly Line A", "station_type": "Assembly"},
    {"station_id": "S2", "name": "Assembly Line B", "station_type": "Assembly"},
    {"station_id": "S3", "name": "Quality Control 1", "station_type": "Quality Check"},
    {"station_id": "S4", "name": "Quality Control 2", "station_type": "Quality Check"},
    {"station_id": "S5", "name": "Packaging Station", "station_type": "Packaging"},
    {"station_id": "S6", "name": "Final Inspection", "station_type": "Inspection"},
]


def seed_sample_data(db: Session) -> Tuple[int, int]:
    """
    Seed the database with sample workers and workstations.
    Skips entries that already exist.
    
    Args:
        db: Database session
        
    Returns:
        Tuple of (workers_created, workstations_created)
    """
    workers_created = 0
    workstations_created = 0
    
    # Create workers
    for worker_data in SAMPLE_WORKERS:
        existing = db.query(Worker).filter(Worker.worker_id == worker_data["worker_id"]).first()
        if not existing:
            db.add(Worker(**worker_data))
            workers_created += 1
    
    # Create workstations
    for station_data in SAMPLE_WORKSTATIONS:
        existing = db.query(Workstation).filter(Workstation.station_id == station_data["station_id"]).first()
        if not existing:
            db.add(Workstation(**station_data))
            workstations_created += 1
    
    db.commit()
    return workers_created, workstations_created


def generate_dummy_events(
    db: Session,
    num_days: int = 7,
    events_per_day: int = 100,
    clear_existing: bool = False
) -> int:
    """
    Generate realistic dummy event data.
    
    The generator simulates:
    - Work shifts (8 hours, starting at 8 AM)
    - Realistic work patterns (more working during peak hours)
    - Production counts correlated with working events
    - Various confidence scores
    
    Args:
        db: Database session
        num_days: Number of days of data to generate
        events_per_day: Approximate events per day per worker
        clear_existing: Whether to clear existing events first
        
    Returns:
        Number of events generated
    """
    # Optionally clear existing events
    if clear_existing:
        db.query(Event).delete()
        db.commit()
    
    # Get workers and workstations
    workers = db.query(Worker).all()
    workstations = db.query(Workstation).all()
    
    if not workers or not workstations:
        raise ValueError("No workers or workstations found. Seed sample data first.")
    
    worker_ids = [w.worker_id for w in workers]
    station_ids = [s.station_id for s in workstations]
    
    events_created = 0
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=num_days)
    
    # Generate events for each day
    current_date = start_date
    while current_date < end_date:
        # Generate events for work shift (8 AM to 4 PM)
        shift_start = current_date.replace(hour=8, minute=0, second=0, microsecond=0)
        shift_end = current_date.replace(hour=16, minute=0, second=0, microsecond=0)
        
        # Calculate event interval based on events_per_day
        shift_duration_minutes = 8 * 60  # 480 minutes
        interval_minutes = shift_duration_minutes / (events_per_day / len(worker_ids))
        
        # Generate events throughout the shift
        event_time = shift_start
        while event_time < shift_end:
            for worker_id in worker_ids:
                # Assign worker to a workstation (workers tend to stay at same station)
                worker_index = worker_ids.index(worker_id)
                primary_station = station_ids[worker_index % len(station_ids)]
                
                # 80% chance to be at primary station
                station_id = primary_station if random.random() < 0.8 else random.choice(station_ids)
                
                # Determine event type based on time of day and randomness
                hour = event_time.hour
                
                # Higher working probability during core hours (9 AM - 3 PM)
                if 9 <= hour <= 15:
                    working_prob = 0.75
                else:
                    working_prob = 0.60
                
                rand = random.random()
                if rand < working_prob:
                    event_type = "working"
                elif rand < working_prob + 0.15:
                    event_type = "idle"
                else:
                    event_type = "absent"
                
                # Generate confidence score (higher for clear activities)
                if event_type == "working":
                    confidence = random.uniform(0.85, 0.99)
                elif event_type == "idle":
                    confidence = random.uniform(0.75, 0.95)
                else:
                    confidence = random.uniform(0.80, 0.98)
                
                # Add some timestamp jitter for realism
                timestamp = event_time + timedelta(seconds=random.randint(-30, 30))
                
                try:
                    event = Event(
                        timestamp=timestamp,
                        worker_id=worker_id,
                        workstation_id=station_id,
                        event_type=event_type,
                        confidence=round(confidence, 3),
                        count=0
                    )
                    db.add(event)
                    db.flush()
                    events_created += 1
                    
                    # Generate production events (correlated with working)
                    if event_type == "working" and random.random() < 0.3:
                        # Production event shortly after working event
                        prod_time = timestamp + timedelta(seconds=random.randint(60, 180))
                        units = random.randint(1, 5)
                        
                        prod_event = Event(
                            timestamp=prod_time,
                            worker_id=worker_id,
                            workstation_id=station_id,
                            event_type="product_count",
                            confidence=random.uniform(0.90, 0.99),
                            count=units
                        )
                        db.add(prod_event)
                        db.flush()
                        events_created += 1
                        
                except IntegrityError:
                    db.rollback()
                    # Skip duplicates
                    continue
            
            # Move to next time interval
            event_time += timedelta(minutes=interval_minutes)
        
        # Move to next day
        current_date += timedelta(days=1)
    
    db.commit()
    return events_created


def clear_all_events(db: Session) -> int:
    """
    Clear all events from the database.
    
    Args:
        db: Database session
        
    Returns:
        Number of events deleted
    """
    count = db.query(Event).count()
    db.query(Event).delete()
    db.commit()
    return count




