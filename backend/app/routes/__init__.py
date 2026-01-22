# API Routes module
from .events import router as events_router
from .workers import router as workers_router
from .workstations import router as workstations_router
from .metrics import router as metrics_router
from .data import router as data_router

__all__ = [
    'events_router',
    'workers_router', 
    'workstations_router',
    'metrics_router',
    'data_router'
]




