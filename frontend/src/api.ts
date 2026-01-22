// API client for the AI Worker Productivity Dashboard

import type { DashboardSummary, WorkerMetrics, WorkstationMetrics, SeedDataResult } from './types';

// Production backend URL
const PRODUCTION_API_URL = 'https://ai-worker-productivity-dashboard-production.up.railway.app/api/v1';

// Use VITE_API_BASE_URL env variable, localhost for dev, or production URL as fallback
const API_BASE = import.meta.env.VITE_API_BASE_URL 
  ? `${import.meta.env.VITE_API_BASE_URL}/api/v1`
  : (import.meta.env.DEV ? 'http://localhost:8000/api/v1' : PRODUCTION_API_URL);

async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `API error: ${response.status}`);
  }

  return response.json();
}

// Dashboard API
export async function getDashboard(startTime?: string, endTime?: string): Promise<DashboardSummary> {
  const params = new URLSearchParams();
  if (startTime) params.append('start_time', startTime);
  if (endTime) params.append('end_time', endTime);
  
  const query = params.toString();
  return fetchApi<DashboardSummary>(`/metrics/dashboard${query ? `?${query}` : ''}`);
}

// Worker metrics API
export async function getWorkerMetrics(workerId?: string): Promise<WorkerMetrics | WorkerMetrics[]> {
  if (workerId) {
    return fetchApi<WorkerMetrics>(`/metrics/workers/${workerId}`);
  }
  return fetchApi<WorkerMetrics[]>('/metrics/workers');
}

// Workstation metrics API
export async function getWorkstationMetrics(stationId?: string): Promise<WorkstationMetrics | WorkstationMetrics[]> {
  if (stationId) {
    return fetchApi<WorkstationMetrics>(`/metrics/workstations/${stationId}`);
  }
  return fetchApi<WorkstationMetrics[]>('/metrics/workstations');
}

// Data management API
export async function refreshData(numDays: number = 7, eventsPerDay: number = 100): Promise<SeedDataResult> {
  return fetchApi<SeedDataResult>('/data/refresh', {
    method: 'POST',
    body: JSON.stringify({
      clear_existing: true,
      num_days: numDays,
      events_per_day: eventsPerDay,
    }),
  });
}

export async function initializeData(): Promise<SeedDataResult> {
  return fetchApi<SeedDataResult>('/data/initialize', {
    method: 'POST',
  });
}

