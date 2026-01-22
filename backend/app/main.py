"""
AI-Powered Worker Productivity Dashboard - Backend API

A FastAPI application that ingests AI-generated events from CCTV systems
and computes productivity metrics for workers, workstations, and the factory.

Architecture:
- FastAPI for REST API
- SQLite for persistence
- Pydantic for validation
- SQLAlchemy for ORM

On startup, the application:
1. Initializes the database schema
2. Seeds sample workers and workstations
3. Generates dummy event data (if database is empty)
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db, SessionLocal
from .config import API_PREFIX
from .routes import (
    events_router,
    workers_router,
    workstations_router,
    metrics_router,
    data_router
)
from .services.data_generator import seed_sample_data, generate_dummy_events
from .models import Event


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    
    On startup:
    - Initialize database tables
    - Seed sample data
    - Generate dummy events if database is empty
    """
    # Startup
    print(" Starting AI Worker Productivity Dashboard API...")
    
    # Initialize database
    init_db()
    print(" Database initialized")
    
    # Seed sample data
    db = SessionLocal()
    try:
        workers, stations = seed_sample_data(db)
        if workers > 0 or stations > 0:
            print(f" Seeded {workers} workers and {stations} workstations")
        
        # Generate dummy data if database is empty
        event_count = db.query(Event).count()
        if event_count == 0:
            print(" Generating initial dummy data...")
            events = generate_dummy_events(db, num_days=7, events_per_day=100)
            print(f" Generated {events} events")
        else:
            print(f"Database contains {event_count} events")
    finally:
        db.close()
    
    print("API ready at http://localhost:8000")
    print(" Documentation at http://localhost:8000/docs")
    
    yield  # Application runs here
    
    # Shutdown
    print(" Shutting down...")


# Create FastAPI application
app = FastAPI(
    title="AI Worker Productivity Dashboard API",
    description="""
    Backend API for the AI-Powered Worker Productivity Dashboard.
    
    ## Features
    
    - **Event Ingestion**: Receive AI-generated events from CCTV systems
    - **Metrics Computation**: Calculate productivity metrics for workers, workstations, and factory
    - **Data Management**: Seed sample data and generate dummy events for testing
    
    ## Event Types
    
    - `working`: Worker is actively working
    - `idle`: Worker is present but not working
    - `absent`: Worker is not at workstation
    - `product_count`: Production count event (includes unit count)
    
    ## Metrics
    
    ### Worker Metrics
    - Total active time
    - Total idle time
    - Utilization percentage
    - Units produced
    - Units per hour
    
    ### Workstation Metrics
    - Occupancy time
    - Utilization percentage
    - Total units produced
    - Throughput rate
    
    ### Factory Metrics
    - Total productive time
    - Total production count
    - Average production rate
    - Average utilization
    """,
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(events_router, prefix=API_PREFIX)
app.include_router(workers_router, prefix=API_PREFIX)
app.include_router(workstations_router, prefix=API_PREFIX)
app.include_router(metrics_router, prefix=API_PREFIX)
app.include_router(data_router, prefix=API_PREFIX)


@app.get("/")
def root():
    """Root endpoint with API information."""
    return {
        "name": "AI Worker Productivity Dashboard API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}




