"""
Workstation management API routes.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Workstation
from ..schemas import WorkstationCreate, WorkstationResponse

router = APIRouter(prefix="/workstations", tags=["workstations"])


@router.get("/", response_model=List[WorkstationResponse])
def list_workstations(db: Session = Depends(get_db)):
    """List all workstations."""
    return db.query(Workstation).all()


@router.get("/{station_id}", response_model=WorkstationResponse)
def get_workstation(station_id: str, db: Session = Depends(get_db)):
    """Get a specific workstation by ID."""
    station = db.query(Workstation).filter(Workstation.station_id == station_id).first()
    if not station:
        raise HTTPException(status_code=404, detail=f"Workstation '{station_id}' not found")
    return station


@router.post("/", response_model=WorkstationResponse, status_code=201)
def create_workstation(station: WorkstationCreate, db: Session = Depends(get_db)):
    """Create a new workstation."""
    # Check if workstation already exists
    existing = db.query(Workstation).filter(Workstation.station_id == station.station_id).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Workstation '{station.station_id}' already exists")
    
    db_station = Workstation(**station.model_dump())
    db.add(db_station)
    db.commit()
    db.refresh(db_station)
    return db_station


@router.delete("/{station_id}")
def delete_workstation(station_id: str, db: Session = Depends(get_db)):
    """Delete a workstation."""
    station = db.query(Workstation).filter(Workstation.station_id == station_id).first()
    if not station:
        raise HTTPException(status_code=404, detail=f"Workstation '{station_id}' not found")
    
    db.delete(station)
    db.commit()
    return {"message": f"Workstation '{station_id}' deleted"}




