"""
Metrics computation service.

This module handles all productivity metric calculations.

=== TIME CALCULATION ASSUMPTIONS ===

Since events represent discrete observations from the CV system, we need to infer
time duration. Our approach:

1. EVENT_DURATION_MINUTES (configurable, default 5 minutes):
   - Each event represents activity for this duration
   - If a worker is detected as 'working', we count EVENT_DURATION_MINUTES of work time
   
2. Time-based events (working, idle, absent):
   - Each event = EVENT_DURATION_MINUTES of that activity type
   - This assumes CV system sends events at regular intervals
   
3. Production events (product_count):
   - These are instantaneous counts, not time-based
   - The 'count' field represents units produced
   - Production events are separate from time tracking

4. Utilization calculations:
   - Worker: working_time / (working_time + idle_time) * 100
   - Workstation: working_time / (working_time + idle_time) * 100
   - 'absent' time is excluded from utilization (worker not at station)

=== PRODUCTION AGGREGATION ===

- product_count events contain the number of units produced in that detection
- Total production = SUM of all 'count' values where event_type='product_count'
- Production rate = total_units / active_hours

=== DUPLICATE HANDLING ===

- Events with same (timestamp, worker_id, workstation_id, event_type) are duplicates
- Database unique constraint prevents storing duplicates
- API returns count of skipped duplicates for transparency
"""
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session

from ..models import Worker, Workstation, Event
from ..schemas import (
    WorkerMetrics, WorkstationMetrics, FactoryMetrics, DashboardSummary
)
from ..config import EVENT_DURATION_MINUTES


def compute_worker_metrics(
    db: Session,
    worker_id: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
) -> List[WorkerMetrics]:
    """
    Compute productivity metrics for workers.
    
    Args:
        db: Database session
        worker_id: Optional filter for specific worker
        start_time: Optional start of time range
        end_time: Optional end of time range
        
    Returns:
        List of WorkerMetrics objects
    """
    # Get all workers or specific worker
    workers_query = db.query(Worker)
    if worker_id:
        workers_query = workers_query.filter(Worker.worker_id == worker_id)
    workers = workers_query.all()
    
    results = []
    
    for worker in workers:
        # Build event query with optional time filters
        events_query = db.query(Event).filter(Event.worker_id == worker.worker_id)
        
        if start_time:
            events_query = events_query.filter(Event.timestamp >= start_time)
        if end_time:
            events_query = events_query.filter(Event.timestamp <= end_time)
        
        events = events_query.all()
        
        # Count events by type
        working_count = sum(1 for e in events if e.event_type == 'working')
        idle_count = sum(1 for e in events if e.event_type == 'idle')
        absent_count = sum(1 for e in events if e.event_type == 'absent')
        
        # Calculate production
        total_units = sum(e.count or 0 for e in events if e.event_type == 'product_count')
        
        # Calculate time in minutes
        active_time = working_count * EVENT_DURATION_MINUTES
        idle_time = idle_count * EVENT_DURATION_MINUTES
        absent_time = absent_count * EVENT_DURATION_MINUTES
        
        # Calculate utilization (exclude absent time)
        total_present_time = active_time + idle_time
        utilization = (active_time / total_present_time * 100) if total_present_time > 0 else 0.0
        
        # Calculate units per hour
        active_hours = active_time / 60 if active_time > 0 else 0
        units_per_hour = total_units / active_hours if active_hours > 0 else 0.0
        
        results.append(WorkerMetrics(
            worker_id=worker.worker_id,
            worker_name=worker.name,
            total_active_time_minutes=round(active_time, 2),
            total_idle_time_minutes=round(idle_time, 2),
            total_absent_time_minutes=round(absent_time, 2),
            utilization_percentage=round(utilization, 2),
            total_units_produced=total_units,
            units_per_hour=round(units_per_hour, 2),
            event_count=len(events)
        ))
    
    return results


def compute_workstation_metrics(
    db: Session,
    station_id: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
) -> List[WorkstationMetrics]:
    """
    Compute productivity metrics for workstations.
    
    Args:
        db: Database session
        station_id: Optional filter for specific workstation
        start_time: Optional start of time range
        end_time: Optional end of time range
        
    Returns:
        List of WorkstationMetrics objects
    """
    # Get all workstations or specific one
    stations_query = db.query(Workstation)
    if station_id:
        stations_query = stations_query.filter(Workstation.station_id == station_id)
    stations = stations_query.all()
    
    results = []
    
    for station in stations:
        # Build event query with optional time filters
        events_query = db.query(Event).filter(Event.workstation_id == station.station_id)
        
        if start_time:
            events_query = events_query.filter(Event.timestamp >= start_time)
        if end_time:
            events_query = events_query.filter(Event.timestamp <= end_time)
        
        events = events_query.all()
        
        # Count events by type
        working_count = sum(1 for e in events if e.event_type == 'working')
        idle_count = sum(1 for e in events if e.event_type == 'idle')
        
        # Calculate production
        total_units = sum(e.count or 0 for e in events if e.event_type == 'product_count')
        
        # Calculate time in minutes
        working_time = working_count * EVENT_DURATION_MINUTES
        idle_time = idle_count * EVENT_DURATION_MINUTES
        occupancy_time = working_time + idle_time  # Time station was in use
        
        # Calculate utilization
        utilization = (working_time / occupancy_time * 100) if occupancy_time > 0 else 0.0
        
        # Calculate throughput (units per hour of occupancy)
        occupancy_hours = occupancy_time / 60 if occupancy_time > 0 else 0
        throughput_rate = total_units / occupancy_hours if occupancy_hours > 0 else 0.0
        
        results.append(WorkstationMetrics(
            station_id=station.station_id,
            station_name=station.name,
            station_type=station.station_type,
            occupancy_time_minutes=round(occupancy_time, 2),
            working_time_minutes=round(working_time, 2),
            idle_time_minutes=round(idle_time, 2),
            utilization_percentage=round(utilization, 2),
            total_units_produced=total_units,
            throughput_rate=round(throughput_rate, 2),
            event_count=len(events)
        ))
    
    return results


def compute_factory_metrics(
    db: Session,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
) -> FactoryMetrics:
    """
    Compute factory-wide aggregate metrics.
    
    Args:
        db: Database session
        start_time: Optional start of time range
        end_time: Optional end of time range
        
    Returns:
        FactoryMetrics object with aggregate values
    """
    # Build event query
    events_query = db.query(Event)
    
    if start_time:
        events_query = events_query.filter(Event.timestamp >= start_time)
    if end_time:
        events_query = events_query.filter(Event.timestamp <= end_time)
    
    events = events_query.all()
    
    # Count events by type
    working_count = sum(1 for e in events if e.event_type == 'working')
    idle_count = sum(1 for e in events if e.event_type == 'idle')
    
    # Calculate total production
    total_production = sum(e.count or 0 for e in events if e.event_type == 'product_count')
    
    # Calculate total times
    total_productive_time = working_count * EVENT_DURATION_MINUTES
    total_idle_time = idle_count * EVENT_DURATION_MINUTES
    
    # Calculate average production rate (units per hour)
    productive_hours = total_productive_time / 60 if total_productive_time > 0 else 0
    avg_production_rate = total_production / productive_hours if productive_hours > 0 else 0.0
    
    # Get worker and workstation metrics for averages
    worker_metrics = compute_worker_metrics(db, start_time=start_time, end_time=end_time)
    station_metrics = compute_workstation_metrics(db, start_time=start_time, end_time=end_time)
    
    # Calculate average utilizations
    active_workers = [w for w in worker_metrics if w.event_count > 0]
    active_stations = [s for s in station_metrics if s.event_count > 0]
    
    avg_worker_util = (
        sum(w.utilization_percentage for w in active_workers) / len(active_workers)
        if active_workers else 0.0
    )
    
    avg_station_util = (
        sum(s.utilization_percentage for s in active_stations) / len(active_stations)
        if active_stations else 0.0
    )
    
    return FactoryMetrics(
        total_productive_time_minutes=round(total_productive_time, 2),
        total_idle_time_minutes=round(total_idle_time, 2),
        total_production_count=total_production,
        average_production_rate=round(avg_production_rate, 2),
        average_worker_utilization=round(avg_worker_util, 2),
        average_workstation_utilization=round(avg_station_util, 2),
        total_events=len(events),
        active_workers=len(active_workers),
        active_workstations=len(active_stations)
    )


def get_dashboard_summary(
    db: Session,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
) -> DashboardSummary:
    """
    Get complete dashboard data including all metrics.
    
    Args:
        db: Database session
        start_time: Optional start of time range
        end_time: Optional end of time range
        
    Returns:
        DashboardSummary with factory, worker, and workstation metrics
    """
    return DashboardSummary(
        factory_metrics=compute_factory_metrics(db, start_time, end_time),
        worker_metrics=compute_worker_metrics(db, start_time=start_time, end_time=end_time),
        workstation_metrics=compute_workstation_metrics(db, start_time=start_time, end_time=end_time),
        last_updated=datetime.utcnow()
    )




