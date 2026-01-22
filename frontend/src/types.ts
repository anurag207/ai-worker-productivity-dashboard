// API Types for the AI Worker Productivity Dashboard

export interface WorkerMetrics {
  worker_id: string;
  worker_name: string;
  total_active_time_minutes: number;
  total_idle_time_minutes: number;
  total_absent_time_minutes: number;
  utilization_percentage: number;
  total_units_produced: number;
  units_per_hour: number;
  event_count: number;
}

export interface WorkstationMetrics {
  station_id: string;
  station_name: string;
  station_type: string | null;
  occupancy_time_minutes: number;
  working_time_minutes: number;
  idle_time_minutes: number;
  utilization_percentage: number;
  total_units_produced: number;
  throughput_rate: number;
  event_count: number;
}

export interface FactoryMetrics {
  total_productive_time_minutes: number;
  total_idle_time_minutes: number;
  total_production_count: number;
  average_production_rate: number;
  average_worker_utilization: number;
  average_workstation_utilization: number;
  total_events: number;
  active_workers: number;
  active_workstations: number;
}

export interface DashboardSummary {
  factory_metrics: FactoryMetrics;
  worker_metrics: WorkerMetrics[];
  workstation_metrics: WorkstationMetrics[];
  last_updated: string;
}

export interface SeedDataResult {
  workers_created: number;
  workstations_created: number;
  events_generated: number;
  message: string;
}




