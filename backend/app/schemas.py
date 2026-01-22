"""
Pydantic schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator


# ============== Event Schemas ==============

class EventCreate(BaseModel):
    """Schema for creating a new event from CCTV system."""
    timestamp: datetime = Field(..., description="When the event occurred")
    worker_id: str = Field(..., description="Worker identifier (e.g., 'W1')")
    workstation_id: str = Field(..., description="Workstation identifier (e.g., 'S1')")
    event_type: str = Field(..., description="Event type: working, idle, absent, product_count")
    confidence: float = Field(..., ge=0.0, le=1.0, description="AI confidence score")
    count: Optional[int] = Field(default=0, ge=0, description="Units produced (for product_count events)")
    
    @validator('event_type')
    def validate_event_type(cls, v):
        allowed_types = ['working', 'idle', 'absent', 'product_count']
        if v not in allowed_types:
            raise ValueError(f'event_type must be one of: {allowed_types}')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2026-01-15T10:15:00Z",
                "worker_id": "W1",
                "workstation_id": "S3",
                "event_type": "working",
                "confidence": 0.93,
                "count": 1
            }
        }


class EventResponse(BaseModel):
    """Schema for event response."""
    id: int
    timestamp: datetime
    worker_id: str
    workstation_id: str
    event_type: str
    confidence: float
    count: Optional[int]
    received_at: datetime
    
    class Config:
        from_attributes = True


class EventBatchCreate(BaseModel):
    """Schema for batch event ingestion."""
    events: List[EventCreate] = Field(..., min_length=1, max_length=1000)


class EventIngestionResult(BaseModel):
    """Result of event ingestion."""
    total_received: int
    successfully_stored: int
    duplicates_skipped: int
    errors: List[str]


# ============== Worker Schemas ==============

class WorkerBase(BaseModel):
    """Base worker schema."""
    worker_id: str
    name: str


class WorkerCreate(WorkerBase):
    """Schema for creating a worker."""
    pass


class WorkerResponse(WorkerBase):
    """Schema for worker response."""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class WorkerMetrics(BaseModel):
    """
    Worker-level productivity metrics.
    
    Metric Definitions:
    - total_active_time_minutes: Total time spent in 'working' state
    - total_idle_time_minutes: Total time spent in 'idle' state
    - utilization_percentage: (active_time / (active_time + idle_time)) * 100
    - total_units_produced: Sum of all product_count events
    - units_per_hour: total_units_produced / (total_active_time in hours)
    """
    worker_id: str
    worker_name: str
    total_active_time_minutes: float
    total_idle_time_minutes: float
    total_absent_time_minutes: float
    utilization_percentage: float
    total_units_produced: int
    units_per_hour: float
    event_count: int


# ============== Workstation Schemas ==============

class WorkstationBase(BaseModel):
    """Base workstation schema."""
    station_id: str
    name: str
    station_type: Optional[str] = None


class WorkstationCreate(WorkstationBase):
    """Schema for creating a workstation."""
    pass


class WorkstationResponse(WorkstationBase):
    """Schema for workstation response."""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class WorkstationMetrics(BaseModel):
    """
    Workstation-level productivity metrics.
    
    Metric Definitions:
    - occupancy_time_minutes: Total time the workstation was occupied (working + idle)
    - utilization_percentage: (working_time / occupancy_time) * 100
    - total_units_produced: Sum of product_count events at this station
    - throughput_rate: units_produced / occupancy_time_hours (units per hour)
    """
    station_id: str
    station_name: str
    station_type: Optional[str]
    occupancy_time_minutes: float
    working_time_minutes: float
    idle_time_minutes: float
    utilization_percentage: float
    total_units_produced: int
    throughput_rate: float
    event_count: int


# ============== Factory Metrics Schemas ==============

class FactoryMetrics(BaseModel):
    """
    Factory-level aggregate metrics.
    
    Metric Definitions:
    - total_productive_time_minutes: Sum of all working time across all workers
    - total_production_count: Total units produced across all workstations
    - average_production_rate: total_production / total_productive_time_hours
    - average_worker_utilization: Mean utilization across all workers
    - average_workstation_utilization: Mean utilization across all workstations
    """
    total_productive_time_minutes: float
    total_idle_time_minutes: float
    total_production_count: int
    average_production_rate: float  # units per hour
    average_worker_utilization: float
    average_workstation_utilization: float
    total_events: int
    active_workers: int
    active_workstations: int


# ============== Dashboard Schemas ==============

class DashboardSummary(BaseModel):
    """Complete dashboard data."""
    factory_metrics: FactoryMetrics
    worker_metrics: List[WorkerMetrics]
    workstation_metrics: List[WorkstationMetrics]
    last_updated: datetime


# ============== Data Management Schemas ==============

class SeedDataResult(BaseModel):
    """Result of seeding sample data."""
    workers_created: int
    workstations_created: int
    events_generated: int
    message: str


class RefreshDataRequest(BaseModel):
    """Request to refresh dummy data."""
    clear_existing: bool = Field(default=False, description="Whether to clear existing events")
    num_days: int = Field(default=7, ge=1, le=30, description="Number of days of data to generate")
    events_per_day: int = Field(default=100, ge=10, le=1000, description="Events per day to generate")




