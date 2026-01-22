"""
SQLAlchemy database models for the productivity dashboard.

Schema Design:
- Workers: Represents factory workers
- Workstations: Represents physical workstations in the factory
- Events: Stores all AI-generated events from CCTV systems

The Events table is designed to handle:
- High-frequency inserts from multiple cameras
- Efficient querying for metrics computation
- Deduplication via unique constraints
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from .database import Base


class Worker(Base):
    """
    Represents a factory worker.
    
    Attributes:
        worker_id: Unique identifier (e.g., 'W1', 'W2')
        name: Worker's display name
        created_at: Timestamp when record was created
    """
    __tablename__ = "workers"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    worker_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to events
    events = relationship("Event", back_populates="worker")
    
    def __repr__(self):
        return f"<Worker(worker_id='{self.worker_id}', name='{self.name}')>"


class Workstation(Base):
    """
    Represents a physical workstation in the factory.
    
    Attributes:
        station_id: Unique identifier (e.g., 'S1', 'S2')
        name: Workstation's display name
        station_type: Type of workstation (e.g., 'Assembly', 'Quality Check')
        created_at: Timestamp when record was created
    """
    __tablename__ = "workstations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    station_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    station_type = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to events
    events = relationship("Event", back_populates="workstation")
    
    def __repr__(self):
        return f"<Workstation(station_id='{self.station_id}', name='{self.name}')>"


class Event(Base):
    """
    Stores AI-generated events from CCTV computer vision system.
    
    Attributes:
        timestamp: When the event occurred (from the CV system)
        worker_id: Reference to the worker
        workstation_id: Reference to the workstation
        event_type: Type of event ('working', 'idle', 'absent', 'product_count')
        confidence: AI model's confidence score (0.0 - 1.0)
        count: For 'product_count' events, the number of units produced
        received_at: When the event was received by the backend (for ordering)
        
    Indexes:
        - Composite index on (worker_id, timestamp) for worker metrics queries
        - Composite index on (workstation_id, timestamp) for workstation metrics queries
        - Index on event_type for filtering
        
    Deduplication:
        - Unique constraint on (timestamp, worker_id, workstation_id, event_type)
        - Prevents exact duplicate events from being stored
    """
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    worker_id = Column(String(50), ForeignKey("workers.worker_id"), nullable=False)
    workstation_id = Column(String(50), ForeignKey("workstations.station_id"), nullable=False)
    event_type = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=False, default=0.0)
    count = Column(Integer, nullable=True, default=0)
    received_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    worker = relationship("Worker", back_populates="events")
    workstation = relationship("Workstation", back_populates="events")
    
    # Table-level constraints and indexes
    __table_args__ = (
        # Unique constraint for deduplication
        UniqueConstraint(
            'timestamp', 'worker_id', 'workstation_id', 'event_type',
            name='uq_event_dedup'
        ),
        # Composite indexes for efficient queries
        Index('ix_events_worker_timestamp', 'worker_id', 'timestamp'),
        Index('ix_events_workstation_timestamp', 'workstation_id', 'timestamp'),
        Index('ix_events_type', 'event_type'),
    )
    
    def __repr__(self):
        return f"<Event(timestamp='{self.timestamp}', worker='{self.worker_id}', type='{self.event_type}')>"




