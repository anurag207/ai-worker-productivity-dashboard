"""
Worker management API routes.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Worker
from ..schemas import WorkerCreate, WorkerResponse

router = APIRouter(prefix="/workers", tags=["workers"])


@router.get("/", response_model=List[WorkerResponse])
def list_workers(db: Session = Depends(get_db)):
    """List all workers."""
    return db.query(Worker).all()


@router.get("/{worker_id}", response_model=WorkerResponse)
def get_worker(worker_id: str, db: Session = Depends(get_db)):
    """Get a specific worker by ID."""
    worker = db.query(Worker).filter(Worker.worker_id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail=f"Worker '{worker_id}' not found")
    return worker


@router.post("/", response_model=WorkerResponse, status_code=201)
def create_worker(worker: WorkerCreate, db: Session = Depends(get_db)):
    """Create a new worker."""
    # Check if worker already exists
    existing = db.query(Worker).filter(Worker.worker_id == worker.worker_id).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Worker '{worker.worker_id}' already exists")
    
    db_worker = Worker(**worker.model_dump())
    db.add(db_worker)
    db.commit()
    db.refresh(db_worker)
    return db_worker


@router.delete("/{worker_id}")
def delete_worker(worker_id: str, db: Session = Depends(get_db)):
    """Delete a worker."""
    worker = db.query(Worker).filter(Worker.worker_id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail=f"Worker '{worker_id}' not found")
    
    db.delete(worker)
    db.commit()
    return {"message": f"Worker '{worker_id}' deleted"}




