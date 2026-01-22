# AI-Powered Worker Productivity Dashboard

A full-stack web application that ingests AI-generated events from CCTV computer vision systems and displays real-time productivity metrics for a manufacturing factory.

## 📋 Table of Contents

- [Overview](#overview)
- [How It Works](#how-it-works)
- [Quick Start](#quick-start)
- [Complete API Usage Examples](#complete-api-usage-examples)
- [Architecture](#architecture)
- [Database Schema](#database-schema)
- [API Documentation](#api-documentation)
- [Metric Definitions](#metric-definitions)
- [Assumptions and Tradeoffs](#assumptions-and-tradeoffs)
- [Edge Cases Handling](#edge-cases-handling)
- [Scalability Considerations](#scalability-considerations)
- [Model Operations](#model-operations)
- [Development](#development)

---

## Overview

This dashboard provides real-time visibility into factory worker productivity by processing events from AI-powered CCTV cameras. The computer vision system detects worker activities and sends structured events that are stored, aggregated, and visualized.

### Features

- **Real-time Event Ingestion**: REST API to receive events from CV systems
- **Batch Processing**: Support for buffered event uploads
- **Comprehensive Metrics**: Worker, workstation, and factory-level analytics
- **Interactive Dashboard**: Modern React UI with filtering and details
- **Data Management**: APIs to seed and refresh data for testing
- **Containerized**: Docker support for easy deployment

### Sample Setup

The system is pre-configured with:
- **6 Workers**: W1-W6 (John Martinez, Sarah Chen, Michael Johnson, Emily Davis, Robert Kim, Lisa Thompson)
- **6 Workstations**: S1-S6 (Assembly Lines, Quality Control, Packaging, Inspection)

---

## How It Works

### Step-by-Step Flow

1. **Event Generation** (Simulated by AI CCTV)
   - Computer vision cameras detect worker activities
   - Each detection generates an event with: timestamp, worker_id, workstation_id, event_type, confidence
   - Event types: `working`, `idle`, `absent`, `product_count`

2. **Event Ingestion** (Backend API)
   - Events are sent to `POST /api/v1/events` (single) or `POST /api/v1/events/batch` (bulk)
   - Backend validates, deduplicates, and stores events in SQLite database
   - Each event is timestamped with both original time and received time

3. **Metrics Computation** (Backend Services)
   - When metrics are requested, the backend queries stored events
   - Calculates worker metrics: active time, idle time, utilization, units produced
   - Calculates workstation metrics: occupancy, utilization, throughput
   - Aggregates factory-level summary statistics

4. **Dashboard Display** (React Frontend)
   - Frontend calls `GET /api/v1/metrics/dashboard` every 30 seconds
   - Displays factory summary cards at the top
   - Shows worker and workstation tables with individual metrics
   - Allows filtering by clicking on specific workers/workstations

### Example Workflow

```bash
# 1. Start the application
docker-compose up --build

# 2. The system auto-generates dummy data on startup
#    Check the logs for: "✅ Generated 872 events"

# 3. View the dashboard
#    Open http://localhost:3000 in your browser

# 4. Refresh data via API (generates new random events)
curl -X POST http://localhost:8000/api/v1/data/refresh

# 5. Manually add a new event
curl -X POST http://localhost:8000/api/v1/events \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2026-01-22T10:00:00Z",
    "worker_id": "W1",
    "workstation_id": "S1",
    "event_type": "working",
    "confidence": 0.95,
    "count": 0
  }'

# 6. Add a production count event
curl -X POST http://localhost:8000/api/v1/events \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2026-01-22T10:05:00Z",
    "worker_id": "W1",
    "workstation_id": "S1",
    "event_type": "product_count",
    "confidence": 0.98,
    "count": 5
  }'

# 7. Get metrics for a specific worker
curl http://localhost:8000/api/v1/metrics/workers/W1

# 8. Get factory-level summary
curl http://localhost:8000/api/v1/metrics/factory
```

---

## Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd ai-worker-productivity-dashboard

# Start all services
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Manual Setup

**Backend:**
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### Refresh Data

Data can be refreshed via the API without editing the database:

```bash
# Initialize with sample data (workers, workstations, 7 days of events)
curl -X POST http://localhost:8000/api/v1/data/initialize

# Refresh with new random data
curl -X POST http://localhost:8000/api/v1/data/refresh

# Generate custom amount of data
curl -X POST http://localhost:8000/api/v1/data/generate-events \
  -H "Content-Type: application/json" \
  -d '{"num_days": 14, "events_per_day": 200, "clear_existing": true}'
```

---

## Complete API Usage Examples

### 1. Ingest Single Event

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/events \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2026-01-22T10:15:00Z",
    "worker_id": "W1",
    "workstation_id": "S3",
    "event_type": "working",
    "confidence": 0.93,
    "count": 0
  }'
```

**Response:**
```json
{
  "id": 1,
  "timestamp": "2026-01-22T10:15:00Z",
  "worker_id": "W1",
  "workstation_id": "S3",
  "event_type": "working",
  "confidence": 0.93,
  "count": 0,
  "received_at": "2026-01-22T10:15:01Z"
}
```

### 2. Ingest Batch Events

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/events/batch \
  -H "Content-Type: application/json" \
  -d '{
    "events": [
      {"timestamp": "2026-01-22T10:00:00Z", "worker_id": "W1", "workstation_id": "S1", "event_type": "working", "confidence": 0.95, "count": 0},
      {"timestamp": "2026-01-22T10:00:00Z", "worker_id": "W2", "workstation_id": "S2", "event_type": "idle", "confidence": 0.88, "count": 0},
      {"timestamp": "2026-01-22T10:05:00Z", "worker_id": "W1", "workstation_id": "S1", "event_type": "product_count", "confidence": 0.99, "count": 3}
    ]
  }'
```

**Response:**
```json
{
  "total_received": 3,
  "successfully_stored": 3,
  "duplicates_skipped": 0,
  "errors": []
}
```

### 3. Get Dashboard Metrics

**Request:**
```bash
curl http://localhost:8000/api/v1/metrics/dashboard
```

**Response:**
```json
{
  "factory": {
    "total_productive_time_hours": 45.5,
    "total_production_count": 1250,
    "avg_production_rate": 27.47,
    "avg_worker_utilization": 72.3,
    "avg_workstation_utilization": 68.5,
    "total_events": 872
  },
  "workers": [
    {
      "worker_id": "W1",
      "name": "John Martinez",
      "total_active_time_hours": 8.5,
      "total_idle_time_hours": 2.1,
      "utilization_percentage": 80.2,
      "total_units_produced": 215,
      "units_per_hour": 25.3
    }
  ],
  "workstations": [
    {
      "station_id": "S1",
      "name": "Assembly Line A",
      "station_type": "Assembly",
      "occupancy_time_hours": 10.2,
      "utilization_percentage": 75.5,
      "total_units_produced": 320,
      "throughput_rate": 31.4
    }
  ]
}
```

### 4. Get Worker Metrics with Time Filter

**Request:**
```bash
curl "http://localhost:8000/api/v1/metrics/workers/W1?start_time=2026-01-20T00:00:00Z&end_time=2026-01-22T23:59:59Z"
```

### 5. Refresh Data

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/data/refresh
```

**Response:**
```json
{
  "message": "Data refreshed successfully",
  "events_generated": 872,
  "workers": 6,
  "workstations": 6
}
```

---

## Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              EDGE LAYER                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │  Camera 1   │  │  Camera 2   │  │  Camera 3   │  │  Camera N   │    │
│  │  + CV Model │  │  + CV Model │  │  + CV Model │  │  + CV Model │    │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘    │
│         │                │                │                │            │
│         └────────────────┴────────────────┴────────────────┘            │
│                                   │                                      │
│                          ┌────────▼────────┐                            │
│                          │   Edge Gateway  │                            │
│                          │  (Aggregation)  │                            │
│                          └────────┬────────┘                            │
└───────────────────────────────────│─────────────────────────────────────┘
                                    │
                          ┌─────────▼─────────┐
                          │   Event Buffer    │
                          │  (Retry Queue)    │
                          └─────────┬─────────┘
                                    │
                          HTTPS/REST│API
                                    │
┌───────────────────────────────────│─────────────────────────────────────┐
│                            BACKEND LAYER                                 │
│                          ┌─────────▼─────────┐                          │
│                          │    FastAPI        │                          │
│                          │  REST API Server  │                          │
│                          └─────────┬─────────┘                          │
│                                    │                                     │
│              ┌─────────────────────┼─────────────────────┐              │
│              │                     │                     │              │
│     ┌────────▼────────┐   ┌────────▼────────┐   ┌────────▼────────┐    │
│     │ Event Ingestion │   │ Metrics Engine  │   │ Data Management │    │
│     │    Service      │   │    Service      │   │    Service      │    │
│     └────────┬────────┘   └────────┬────────┘   └────────┬────────┘    │
│              │                     │                     │              │
│              └─────────────────────┼─────────────────────┘              │
│                                    │                                     │
│                          ┌─────────▼─────────┐                          │
│                          │     SQLite        │                          │
│                          │    Database       │                          │
│                          └───────────────────┘                          │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                              REST API
                                    │
┌───────────────────────────────────│─────────────────────────────────────┐
│                           FRONTEND LAYER                                 │
│                          ┌─────────▼─────────┐                          │
│                          │    React App      │                          │
│                          │   (Dashboard)     │                          │
│                          └───────────────────┘                          │
│                                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                   │
│  │Factory Stats │  │Worker Metrics│  │Station Metrics│                  │
│  └──────────────┘  └──────────────┘  └──────────────┘                   │
└─────────────────────────────────────────────────────────────────────────┘
```

### Component Descriptions

| Component | Technology | Purpose |
|-----------|------------|---------|
| Edge Layer | CV Models on cameras | Detect worker activities, generate events |
| Edge Gateway | IoT Gateway | Aggregate events, handle connectivity |
| Backend API | FastAPI (Python) | REST API for ingestion and queries |
| Database | SQLite | Persistent storage for events and metadata |
| Frontend | React + TypeScript | Interactive dashboard visualization |

### Data Flow

1. **Event Generation**: CV models on cameras detect activities (working, idle, absent, production)
2. **Edge Processing**: Events are timestamped and buffered at the edge gateway
3. **Transmission**: Events sent to backend via REST API (single or batch)
4. **Storage**: Events persisted to SQLite with deduplication
5. **Computation**: Metrics computed on-demand from stored events
6. **Visualization**: Dashboard fetches and displays metrics

---

## Database Schema

### Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│     Workers     │       │     Events      │       │  Workstations   │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │       │ id (PK)         │
│ worker_id (UK)  │◄──────│ worker_id (FK)  │       │ station_id (UK) │
│ name            │       │ workstation_id (FK)────►│ name            │
│ created_at      │       │ timestamp       │       │ station_type    │
└─────────────────┘       │ event_type      │       │ created_at      │
                          │ confidence      │       └─────────────────┘
                          │ count           │
                          │ received_at     │
                          └─────────────────┘
```

### Tables

#### Workers
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key (auto-increment) |
| worker_id | VARCHAR(50) | Unique business identifier (e.g., "W1") |
| name | VARCHAR(100) | Worker's display name |
| created_at | DATETIME | Record creation timestamp |

#### Workstations
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key (auto-increment) |
| station_id | VARCHAR(50) | Unique business identifier (e.g., "S1") |
| name | VARCHAR(100) | Workstation display name |
| station_type | VARCHAR(100) | Type (Assembly, Quality Check, etc.) |
| created_at | DATETIME | Record creation timestamp |

#### Events
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key (auto-increment) |
| timestamp | DATETIME | When event occurred (from CV system) |
| worker_id | VARCHAR(50) | Foreign key to workers |
| workstation_id | VARCHAR(50) | Foreign key to workstations |
| event_type | VARCHAR(50) | working, idle, absent, product_count |
| confidence | FLOAT | AI model confidence (0.0-1.0) |
| count | INTEGER | Units produced (for product_count events) |
| received_at | DATETIME | When backend received the event |

### Indexes

- `ix_events_worker_timestamp`: Composite index for worker metric queries
- `ix_events_workstation_timestamp`: Composite index for workstation queries
- `ix_events_type`: Index for filtering by event type
- Unique constraint on `(timestamp, worker_id, workstation_id, event_type)` for deduplication

---

## API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Endpoints

#### Event Ingestion

**POST /events** - Ingest single event
```json
{
  "timestamp": "2026-01-15T10:15:00Z",
  "worker_id": "W1",
  "workstation_id": "S3",
  "event_type": "working",
  "confidence": 0.93,
  "count": 0
}
```

**POST /events/batch** - Ingest multiple events
```json
{
  "events": [
    {"timestamp": "...", "worker_id": "W1", ...},
    {"timestamp": "...", "worker_id": "W2", ...}
  ]
}
```

#### Metrics

**GET /metrics/dashboard** - Complete dashboard data
**GET /metrics/factory** - Factory-level aggregates
**GET /metrics/workers** - All worker metrics
**GET /metrics/workers/{worker_id}** - Single worker metrics
**GET /metrics/workstations** - All workstation metrics
**GET /metrics/workstations/{station_id}** - Single workstation metrics

All metrics endpoints support optional query parameters:
- `start_time`: Filter events after this timestamp
- `end_time`: Filter events before this timestamp

#### Data Management

**POST /data/seed** - Create sample workers and workstations
**POST /data/initialize** - Seed + generate 7 days of events
**POST /data/generate-events** - Generate custom events
**POST /data/refresh** - Clear and regenerate all events
**DELETE /data/events** - Clear all events

### Interactive Documentation

Visit `http://localhost:8000/docs` for Swagger UI documentation.

---

## Metric Definitions

### Worker-Level Metrics

| Metric | Formula | Description |
|--------|---------|-------------|
| Total Active Time | `working_events × EVENT_DURATION` | Time spent in 'working' state |
| Total Idle Time | `idle_events × EVENT_DURATION` | Time spent in 'idle' state |
| Utilization % | `active_time / (active_time + idle_time) × 100` | Percentage of present time spent working |
| Total Units Produced | `SUM(count) WHERE event_type='product_count'` | Total production output |
| Units Per Hour | `total_units / (active_time_hours)` | Production rate during active time |

### Workstation-Level Metrics

| Metric | Formula | Description |
|--------|---------|-------------|
| Occupancy Time | `(working_events + idle_events) × EVENT_DURATION` | Total time station was in use |
| Utilization % | `working_time / occupancy_time × 100` | Efficiency of occupied time |
| Total Units Produced | `SUM(count) WHERE event_type='product_count'` | Output at this station |
| Throughput Rate | `total_units / occupancy_time_hours` | Units per hour of occupancy |

### Factory-Level Metrics

| Metric | Formula | Description |
|--------|---------|-------------|
| Total Productive Time | `SUM(working_time) across all workers` | Factory-wide working time |
| Total Production Count | `SUM(units) across all stations` | Total factory output |
| Avg Production Rate | `total_production / productive_hours` | Factory units per hour |
| Avg Worker Utilization | `MEAN(worker_utilization)` | Average worker efficiency |
| Avg Workstation Utilization | `MEAN(station_utilization)` | Average station efficiency |

---

## Assumptions and Tradeoffs

### Time Duration Calculation

**Assumption**: Each event represents activity for a fixed duration (default: 5 minutes).

**Rationale**: Since CV systems send discrete detection events rather than continuous streams, we need to infer duration. We assume the CV system sends periodic snapshots at regular intervals.

**Configuration**: `EVENT_DURATION_MINUTES` in `config.py` (default: 5)

**Alternative approaches considered**:
1. Calculate duration between consecutive events (more accurate but complex)
2. Event-start/event-end pairs (requires CV system changes)
3. Sliding windows (higher complexity)

### Production Event Aggregation

**How production events relate to time-based events**:

1. `product_count` events are **instantaneous** - they record units produced at a moment
2. Time-based events (`working`, `idle`, `absent`) represent **state during a period**
3. Production typically occurs during `working` state
4. The `count` field in `product_count` events is summed for totals
5. Production rate is calculated as: `total_units / active_hours`

**Example**:
```
10:00 - working (W1 at S1)
10:02 - product_count (W1 at S1, count=3)  ← 3 units produced
10:05 - working (W1 at S1)
10:08 - product_count (W1 at S1, count=2)  ← 2 more units
10:10 - idle (W1 at S1)
```
Result: W1 produced 5 units in 10 minutes of active time = 30 units/hour rate

### Utilization Calculation

**Excluded from utilization**: `absent` time is not counted in utilization calculations.

**Rationale**: Utilization measures efficiency while present. A worker away from their station (break, meeting, etc.) shouldn't penalize their utilization score.

---

## Edge Cases Handling

### 1. Intermittent Connectivity

**Problem**: Edge devices may lose network connectivity temporarily.

**Solution**:
- **Edge-side buffering**: Events stored locally when offline
- **Batch API**: `POST /events/batch` accepts up to 1000 events
- **Idempotent processing**: Duplicates are silently handled
- **Received timestamp**: Separate from event timestamp for ordering

**Implementation**:
```python
# Backend accepts batch uploads
@router.post("/events/batch")
def ingest_events_batch(batch: EventBatchCreate):
    # Process each event individually
    # Skip duplicates, log errors
    # Return summary of results
```

**Recommended edge architecture**:
```
[Camera] → [Local Buffer] → [Retry Queue] → [Backend API]
                ↑                  │
                └──────────────────┘ (on failure)
```

### 2. Duplicate Events

**Problem**: Network retries or system issues may cause duplicate submissions.

**Solution**:
- **Database constraint**: Unique on `(timestamp, worker_id, workstation_id, event_type)`
- **Graceful handling**: Duplicates return success (idempotent)
- **Monitoring**: API returns duplicate count for observability

**Example response**:
```json
{
  "total_received": 100,
  "successfully_stored": 95,
  "duplicates_skipped": 5,
  "errors": []
}
```

### 3. Out-of-Order Timestamps

**Problem**: Events may arrive out of chronological order due to:
- Network latency variations
- Batch uploads of buffered events
- Multiple edge gateways

**Solution**:
- **Store original timestamp**: `timestamp` field preserves event time
- **Record arrival time**: `received_at` captures when backend received it
- **Query flexibility**: Metrics queries use event timestamp by default
- **No reordering requirement**: Events don't need sequential processing

**How metrics handle this**:
```python
# Metrics are computed from all events in time range
# Order doesn't matter - we count events by type
events = query.filter(Event.timestamp >= start_time)
working_count = sum(1 for e in events if e.event_type == 'working')
```

---

## Scalability Considerations

### Current Architecture (5 Cameras)

- **Backend**: Single FastAPI instance
- **Database**: SQLite (single file)
- **Capacity**: ~1000 events/minute
- **Suitable for**: Small factory, demo, development

### Medium Scale (100+ Cameras)

**Recommended changes**:

1. **Database Migration**:
   ```
   SQLite → PostgreSQL
   ```
   - Better concurrency handling
   - Connection pooling
   - ACID compliance at scale

2. **API Scaling**:
   ```
   Single Instance → Load Balanced Cluster
   
   [Load Balancer]
         │
   ┌─────┼─────┐
   │     │     │
   [API] [API] [API]
         │
   [PostgreSQL]
   ```

3. **Event Processing**:
   ```
   Sync Processing → Async Queue
   
   [API] → [Redis/RabbitMQ] → [Worker Pool] → [Database]
   ```

4. **Caching**:
   - Redis for computed metrics (TTL: 30 seconds)
   - Reduces database load for dashboard refreshes

### Enterprise Scale (Multi-Site)

**Architecture evolution**:

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   Site A    │  │   Site B    │  │   Site C    │
│ Edge + API  │  │ Edge + API  │  │ Edge + API  │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │
       └────────────────┼────────────────┘
                        │
              ┌─────────▼─────────┐
              │  Central Gateway  │
              │   (Kafka/Kinesis) │
              └─────────┬─────────┘
                        │
              ┌─────────▼─────────┐
              │  Data Lake/DW     │
              │  (TimescaleDB)    │
              └─────────┬─────────┘
                        │
              ┌─────────▼─────────┐
              │   Analytics       │
              │   Dashboard       │
              └───────────────────┘
```

**Key components**:

1. **Event Streaming**: Apache Kafka or AWS Kinesis
   - Handles millions of events/second
   - Guaranteed delivery
   - Replay capability

2. **Time-Series Database**: TimescaleDB or InfluxDB
   - Optimized for time-series queries
   - Automatic data retention policies
   - Efficient aggregations

3. **Data Partitioning**:
   - Partition by `site_id` and `timestamp`
   - Each site can query independently
   - Central aggregation for enterprise view

4. **Monitoring & Alerting**:
   - Prometheus + Grafana for metrics
   - Alert on ingestion lag
   - Model performance dashboards

---

## Model Operations

### Model Versioning

**Implementation approach**:

1. **Add version tracking to events**:
   ```python
   class Event(Base):
       # ... existing fields ...
       model_id = Column(String(50))      # e.g., "activity-detector-v2.1"
       model_version = Column(String(20)) # e.g., "2.1.0"
   ```

2. **Version metadata table**:
   ```sql
   CREATE TABLE model_versions (
       id SERIAL PRIMARY KEY,
       model_id VARCHAR(50),
       version VARCHAR(20),
       deployed_at TIMESTAMP,
       accuracy FLOAT,
       notes TEXT
   );
   ```

3. **API enhancement**:
   ```json
   {
     "timestamp": "2026-01-15T10:15:00Z",
     "worker_id": "W1",
     "event_type": "working",
     "confidence": 0.93,
     "model_id": "activity-detector",
     "model_version": "2.1.0"
   }
   ```

4. **Benefits**:
   - Track performance per model version
   - Compare v2.0 vs v2.1 accuracy
   - Rollback capability
   - A/B testing support

### Model Drift Detection

**Strategy**:

1. **Confidence Score Monitoring**:
   ```python
   # Alert if average confidence drops
   avg_confidence = db.query(func.avg(Event.confidence))\
       .filter(Event.timestamp > one_hour_ago)\
       .scalar()
   
   if avg_confidence < CONFIDENCE_THRESHOLD:
       trigger_alert("Model confidence degradation detected")
   ```

2. **Distribution Shift Detection**:
   ```python
   # Compare event type distributions
   current_dist = get_event_distribution(last_24h)
   baseline_dist = get_event_distribution(last_30d)
   
   drift_score = calculate_kl_divergence(current_dist, baseline_dist)
   if drift_score > DRIFT_THRESHOLD:
       trigger_alert("Event distribution drift detected")
   ```

3. **Metrics to monitor**:
   | Metric | Normal Range | Alert Threshold |
   |--------|--------------|-----------------|
   | Avg Confidence | 0.85-0.95 | < 0.80 |
   | Working % | 60-75% | < 50% or > 85% |
   | Detection Rate | 10-15/min/camera | < 5 or > 25 |

4. **Dashboard additions**:
   - Confidence trend charts
   - Event type distribution over time
   - Model version performance comparison

### Triggering Retraining

**Automated retraining pipeline**:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Drift      │────►│  Collect    │────►│  Retrain    │
│  Detected   │     │  Samples    │     │  Model      │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
┌─────────────┐     ┌─────────────┐     ┌──────▼──────┐
│  Deploy to  │◄────│  Validate   │◄────│  Evaluate   │
│  Production │     │  A/B Test   │     │  Offline    │
└─────────────┘     └─────────────┘     └─────────────┘
```

**Trigger conditions**:

1. **Performance-based**:
   - Confidence drops below threshold for > 1 hour
   - Significant distribution shift detected
   - Manual labeling shows accuracy < target

2. **Time-based**:
   - Scheduled monthly retraining
   - After significant factory changes (new equipment, layout)

3. **Data-based**:
   - New labeled data reaches threshold (e.g., 1000 samples)
   - New worker/workstation types added

**Implementation example**:

```python
# Drift monitoring job (runs hourly)
def check_for_drift():
    metrics = calculate_drift_metrics()
    
    if metrics['confidence_drift'] > THRESHOLD:
        trigger_retraining(
            reason="confidence_degradation",
            data_range=(start_date, end_date),
            priority="high"
        )
    
    if metrics['distribution_drift'] > THRESHOLD:
        trigger_retraining(
            reason="distribution_shift",
            data_range=(start_date, end_date),
            priority="medium"
        )

def trigger_retraining(reason, data_range, priority):
    # 1. Export training data
    export_labeled_events(data_range)
    
    # 2. Trigger ML pipeline (e.g., via webhook)
    requests.post(ML_PIPELINE_URL, json={
        "reason": reason,
        "data_path": export_path,
        "priority": priority
    })
    
    # 3. Log for tracking
    log_retraining_trigger(reason, data_range)
```

---

## Development

### Project Structure

```
ai-worker-productivity-dashboard/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI application
│   │   ├── config.py         # Configuration settings
│   │   ├── database.py       # Database connection
│   │   ├── models.py         # SQLAlchemy models
│   │   ├── schemas.py        # Pydantic schemas
│   │   ├── routes/           # API endpoints
│   │   │   ├── events.py
│   │   │   ├── workers.py
│   │   │   ├── workstations.py
│   │   │   ├── metrics.py
│   │   │   └── data.py
│   │   └── services/         # Business logic
│   │       ├── metrics.py
│   │       └── data_generator.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.tsx           # Main React component
│   │   ├── api.ts            # API client
│   │   ├── types.ts          # TypeScript types
│   │   └── index.css         # Styles
│   ├── package.json
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
└── README.md
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| DATABASE_URL | sqlite:///./productivity.db | Database connection string |
| EVENT_DURATION_MINUTES | 5 | Duration each event represents |

---

## License

MIT License - See LICENSE file for details.

---

## Contact

For questions or issues, please open a GitHub issue.

