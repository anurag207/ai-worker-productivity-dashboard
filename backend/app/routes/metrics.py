"""
Metrics API routes.

Provides computed productivity metrics for:
- Individual workers
- Individual workstations
- Factory-wide aggregates
- Complete dashboard summary
"""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import WorkerMetrics, WorkstationMetrics, FactoryMetrics, DashboardSummary
from ..services.metrics import (
    compute_worker_metrics,
    compute_workstation_metrics,
    compute_factory_metrics,
    get_dashboard_summary
)

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/dashboard", response_model=DashboardSummary)
def get_dashboard(
    start_time: Optional[datetime] = Query(None, description="Start of time range"),
    end_time: Optional[datetime] = Query(None, description="End of time range"),
    db: Session = Depends(get_db)
):
    """
    Get complete dashboard data.
    
    Returns all metrics needed for the dashboard:
    - Factory-level summary
    - All worker metrics
    - All workstation metrics
    
    Optionally filter by time range.
    """
    return get_dashboard_summary(db, start_time, end_time)


@router.get("/factory", response_model=FactoryMetrics)
def get_factory_metrics(
    start_time: Optional[datetime] = Query(None, description="Start of time range"),
    end_time: Optional[datetime] = Query(None, description="End of time range"),
    db: Session = Depends(get_db)
):
    """
    Get factory-wide aggregate metrics.
    
    Includes:
    - Total productive time
    - Total production count
    - Average production rate
    - Average worker utilization
    - Average workstation utilization
    """
    return compute_factory_metrics(db, start_time, end_time)


@router.get("/workers", response_model=List[WorkerMetrics])
def get_workers_metrics(
    start_time: Optional[datetime] = Query(None, description="Start of time range"),
    end_time: Optional[datetime] = Query(None, description="End of time range"),
    db: Session = Depends(get_db)
):
    """
    Get metrics for all workers.
    
    Each worker's metrics include:
    - Total active time
    - Total idle time
    - Utilization percentage
    - Total units produced
    - Units per hour
    """
    return compute_worker_metrics(db, start_time=start_time, end_time=end_time)


@router.get("/workers/{worker_id}", response_model=WorkerMetrics)
def get_worker_metrics(
    worker_id: str,
    start_time: Optional[datetime] = Query(None, description="Start of time range"),
    end_time: Optional[datetime] = Query(None, description="End of time range"),
    db: Session = Depends(get_db)
):
    """Get metrics for a specific worker."""
    metrics = compute_worker_metrics(db, worker_id, start_time, end_time)
    if not metrics:
        return WorkerMetrics(
            worker_id=worker_id,
            worker_name="Unknown",
            total_active_time_minutes=0,
            total_idle_time_minutes=0,
            total_absent_time_minutes=0,
            utilization_percentage=0,
            total_units_produced=0,
            units_per_hour=0,
            event_count=0
        )
    return metrics[0]


@router.get("/workstations", response_model=List[WorkstationMetrics])
def get_workstations_metrics(
    start_time: Optional[datetime] = Query(None, description="Start of time range"),
    end_time: Optional[datetime] = Query(None, description="End of time range"),
    db: Session = Depends(get_db)
):
    """
    Get metrics for all workstations.
    
    Each workstation's metrics include:
    - Occupancy time
    - Utilization percentage
    - Total units produced
    - Throughput rate
    """
    return compute_workstation_metrics(db, start_time=start_time, end_time=end_time)


@router.get("/workstations/{station_id}", response_model=WorkstationMetrics)
def get_workstation_metrics(
    station_id: str,
    start_time: Optional[datetime] = Query(None, description="Start of time range"),
    end_time: Optional[datetime] = Query(None, description="End of time range"),
    db: Session = Depends(get_db)
):
    """Get metrics for a specific workstation."""
    metrics = compute_workstation_metrics(db, station_id, start_time, end_time)
    if not metrics:
        return WorkstationMetrics(
            station_id=station_id,
            station_name="Unknown",
            station_type=None,
            occupancy_time_minutes=0,
            working_time_minutes=0,
            idle_time_minutes=0,
            utilization_percentage=0,
            total_units_produced=0,
            throughput_rate=0,
            event_count=0
        )
    return metrics[0]




