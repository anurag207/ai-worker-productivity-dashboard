import { useState, useEffect, useCallback } from 'react';
import { 
  Factory, Users, Monitor, TrendingUp, Clock, Package, 
  Activity, RefreshCw, X, AlertCircle, Zap, Target
} from 'lucide-react';
import { getDashboard, refreshData } from './api';
import type { DashboardSummary, WorkerMetrics, WorkstationMetrics } from './types';

function App() {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedWorker, setSelectedWorker] = useState<WorkerMetrics | null>(null);
  const [selectedWorkstation, setSelectedWorkstation] = useState<WorkstationMetrics | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setError(null);
      const dashboard = await getDashboard();
      setData(dashboard);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch dashboard data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [fetchData]);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await refreshData(7, 100);
      await fetchData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to refresh data');
    } finally {
      setRefreshing(false);
    }
  };

  const formatTime = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = Math.round(minutes % 60);
    if (hours === 0) return `${mins}m`;
    return `${hours}h ${mins}m`;
  };

  const formatNumber = (num: number) => {
    return num.toLocaleString();
  };

  const getUtilizationClass = (util: number) => {
    if (util >= 70) return 'high';
    if (util >= 40) return 'medium';
    return 'low';
  };

  const getStationTypeBadgeClass = (type: string | null) => {
    if (!type) return '';
    const t = type.toLowerCase();
    if (t.includes('assembly')) return 'type-assembly';
    if (t.includes('quality')) return 'type-quality';
    if (t.includes('packaging')) return 'type-packaging';
    if (t.includes('inspection')) return 'type-inspection';
    return '';
  };

  if (loading) {
    return (
      <div className="app">
        <div className="loading">
          <div className="loading-spinner" />
          <span className="loading-text">Loading dashboard...</span>
        </div>
      </div>
    );
  }

  if (error && !data) {
    return (
      <div className="app">
        <div className="error">
          <AlertCircle size={24} />
          <span>{error}</span>
        </div>
      </div>
    );
  }

  const factory = data?.factory_metrics;

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <div className="header-title">
            <div className="header-icon">
              <Factory size={28} color="white" />
            </div>
            <div>
              <h1>AI Worker Productivity Dashboard</h1>
              <p>Real-time manufacturing analytics powered by computer vision</p>
            </div>
          </div>
          <div className="header-actions">
            {data && (
              <span className="last-updated">
                Last updated: {new Date(data.last_updated).toLocaleTimeString()}
              </span>
            )}
            <button 
              className="btn btn-primary" 
              onClick={handleRefresh}
              disabled={refreshing}
            >
              <RefreshCw size={18} className={refreshing ? 'spinning' : ''} />
              {refreshing ? 'Refreshing...' : 'Refresh Data'}
            </button>
          </div>
        </div>
      </header>

      {error && (
        <div className="error" style={{ marginBottom: '1.5rem' }}>
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      {/* Factory Summary */}
      <section className="factory-summary">
        <div className="metric-card blue">
          <div className="metric-card-header">
            <div className="metric-card-icon">
              <Clock size={20} color="#3b82f6" />
            </div>
            <span className="metric-card-label">Productive Time</span>
          </div>
          <div className="metric-card-value">
            {formatTime(factory?.total_productive_time_minutes || 0)}
          </div>
          <div className="metric-card-unit">Total working time</div>
        </div>

        <div className="metric-card emerald">
          <div className="metric-card-header">
            <div className="metric-card-icon">
              <Package size={20} color="#10b981" />
            </div>
            <span className="metric-card-label">Total Production</span>
          </div>
          <div className="metric-card-value">
            {formatNumber(factory?.total_production_count || 0)}
          </div>
          <div className="metric-card-unit">Units produced</div>
        </div>

        <div className="metric-card amber">
          <div className="metric-card-header">
            <div className="metric-card-icon">
              <TrendingUp size={20} color="#f59e0b" />
            </div>
            <span className="metric-card-label">Production Rate</span>
          </div>
          <div className="metric-card-value">
            {factory?.average_production_rate?.toFixed(1) || '0'}
          </div>
          <div className="metric-card-unit">Units per hour</div>
        </div>

        <div className="metric-card blue">
          <div className="metric-card-header">
            <div className="metric-card-icon">
              <Target size={20} color="#3b82f6" />
            </div>
            <span className="metric-card-label">Worker Utilization</span>
          </div>
          <div className="metric-card-value">
            {factory?.average_worker_utilization?.toFixed(1) || '0'}%
          </div>
          <div className="metric-card-unit">Average efficiency</div>
        </div>

        <div className="metric-card emerald">
          <div className="metric-card-header">
            <div className="metric-card-icon">
              <Zap size={20} color="#10b981" />
            </div>
            <span className="metric-card-label">Station Utilization</span>
          </div>
          <div className="metric-card-value">
            {factory?.average_workstation_utilization?.toFixed(1) || '0'}%
          </div>
          <div className="metric-card-unit">Average efficiency</div>
        </div>

        <div className="metric-card rose">
          <div className="metric-card-header">
            <div className="metric-card-icon">
              <Activity size={20} color="#f43f5e" />
            </div>
            <span className="metric-card-label">Total Events</span>
          </div>
          <div className="metric-card-value">
            {formatNumber(factory?.total_events || 0)}
          </div>
          <div className="metric-card-unit">AI detections</div>
        </div>
      </section>

      {/* Workers and Workstations */}
      <div className="sections-grid">
        {/* Workers Section */}
        <section className="section">
          <div className="section-header">
            <h2 className="section-title">
              <Users size={20} />
              Workers ({data?.worker_metrics.length || 0})
            </h2>
          </div>
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Worker</th>
                  <th>Utilization</th>
                  <th>Active Time</th>
                  <th>Units</th>
                  <th>Rate</th>
                </tr>
              </thead>
              <tbody>
                {data?.worker_metrics.map((worker) => (
                  <tr 
                    key={worker.worker_id}
                    className={selectedWorker?.worker_id === worker.worker_id ? 'selected' : ''}
                    onClick={() => setSelectedWorker(
                      selectedWorker?.worker_id === worker.worker_id ? null : worker
                    )}
                  >
                    <td>
                      <div className="entity-cell">
                        <div className="entity-avatar">
                          {worker.worker_name.split(' ').map(n => n[0]).join('')}
                        </div>
                        <div className="entity-info">
                          <span className="entity-name">{worker.worker_name}</span>
                          <span className="entity-id">{worker.worker_id}</span>
                        </div>
                      </div>
                    </td>
                    <td>
                      <div className="utilization-cell">
                        <span className="utilization-value">
                          {worker.utilization_percentage.toFixed(1)}%
                        </span>
                        <div className="progress-bar">
                          <div 
                            className={`progress-bar-fill ${getUtilizationClass(worker.utilization_percentage)}`}
                            style={{ width: `${Math.min(worker.utilization_percentage, 100)}%` }}
                          />
                        </div>
                      </div>
                    </td>
                    <td className="mono">{formatTime(worker.total_active_time_minutes)}</td>
                    <td className="mono">{formatNumber(worker.total_units_produced)}</td>
                    <td className="mono">{worker.units_per_hour.toFixed(1)}/hr</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* Workstations Section */}
        <section className="section">
          <div className="section-header">
            <h2 className="section-title">
              <Monitor size={20} />
              Workstations ({data?.workstation_metrics.length || 0})
            </h2>
          </div>
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Station</th>
                  <th>Utilization</th>
                  <th>Occupancy</th>
                  <th>Units</th>
                  <th>Throughput</th>
                </tr>
              </thead>
              <tbody>
                {data?.workstation_metrics.map((station) => (
                  <tr 
                    key={station.station_id}
                    className={selectedWorkstation?.station_id === station.station_id ? 'selected' : ''}
                    onClick={() => setSelectedWorkstation(
                      selectedWorkstation?.station_id === station.station_id ? null : station
                    )}
                  >
                    <td>
                      <div className="entity-cell">
                        <div className="entity-avatar" style={{ 
                          background: station.station_type?.toLowerCase().includes('assembly') 
                            ? 'linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%)'
                            : station.station_type?.toLowerCase().includes('quality')
                            ? 'linear-gradient(135deg, #10b981 0%, #06b6d4 100%)'
                            : station.station_type?.toLowerCase().includes('packaging')
                            ? 'linear-gradient(135deg, #f59e0b 0%, #f97316 100%)'
                            : 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)'
                        }}>
                          {station.station_id}
                        </div>
                        <div className="entity-info">
                          <span className="entity-name">{station.station_name}</span>
                          {station.station_type && (
                            <span className={`badge ${getStationTypeBadgeClass(station.station_type)}`}>
                              {station.station_type}
                            </span>
                          )}
                        </div>
                      </div>
                    </td>
                    <td>
                      <div className="utilization-cell">
                        <span className="utilization-value">
                          {station.utilization_percentage.toFixed(1)}%
                        </span>
                        <div className="progress-bar">
                          <div 
                            className={`progress-bar-fill ${getUtilizationClass(station.utilization_percentage)}`}
                            style={{ width: `${Math.min(station.utilization_percentage, 100)}%` }}
                          />
                        </div>
                      </div>
                    </td>
                    <td className="mono">{formatTime(station.occupancy_time_minutes)}</td>
                    <td className="mono">{formatNumber(station.total_units_produced)}</td>
                    <td className="mono">{station.throughput_rate.toFixed(1)}/hr</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>

      {/* Worker Detail Panel */}
      {selectedWorker && (
        <div className="detail-panel">
          <div className="detail-panel-header">
            <h3 className="detail-panel-title">
              <div className="entity-avatar" style={{ width: 40, height: 40 }}>
                {selectedWorker.worker_name.split(' ').map(n => n[0]).join('')}
              </div>
              {selectedWorker.worker_name}
              <span className="badge">{selectedWorker.worker_id}</span>
            </h3>
            <button className="close-btn" onClick={() => setSelectedWorker(null)}>
              <X size={18} />
            </button>
          </div>
          <div className="detail-grid">
            <div className="detail-item">
              <div className="detail-item-label">Total Active Time</div>
              <div className="detail-item-value">{formatTime(selectedWorker.total_active_time_minutes)}</div>
            </div>
            <div className="detail-item">
              <div className="detail-item-label">Total Idle Time</div>
              <div className="detail-item-value">{formatTime(selectedWorker.total_idle_time_minutes)}</div>
            </div>
            <div className="detail-item">
              <div className="detail-item-label">Total Absent Time</div>
              <div className="detail-item-value">{formatTime(selectedWorker.total_absent_time_minutes)}</div>
            </div>
            <div className="detail-item">
              <div className="detail-item-label">Utilization Rate</div>
              <div className="detail-item-value">{selectedWorker.utilization_percentage.toFixed(1)}%</div>
            </div>
            <div className="detail-item">
              <div className="detail-item-label">Units Produced</div>
              <div className="detail-item-value">{formatNumber(selectedWorker.total_units_produced)}</div>
            </div>
            <div className="detail-item">
              <div className="detail-item-label">Production Rate</div>
              <div className="detail-item-value">{selectedWorker.units_per_hour.toFixed(1)}/hr</div>
            </div>
            <div className="detail-item">
              <div className="detail-item-label">Total Events</div>
              <div className="detail-item-value">{formatNumber(selectedWorker.event_count)}</div>
            </div>
          </div>
        </div>
      )}

      {/* Workstation Detail Panel */}
      {selectedWorkstation && (
        <div className="detail-panel">
          <div className="detail-panel-header">
            <h3 className="detail-panel-title">
              <div className="entity-avatar" style={{ 
                width: 40, 
                height: 40,
                background: selectedWorkstation.station_type?.toLowerCase().includes('assembly') 
                  ? 'linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%)'
                  : selectedWorkstation.station_type?.toLowerCase().includes('quality')
                  ? 'linear-gradient(135deg, #10b981 0%, #06b6d4 100%)'
                  : selectedWorkstation.station_type?.toLowerCase().includes('packaging')
                  ? 'linear-gradient(135deg, #f59e0b 0%, #f97316 100%)'
                  : 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)'
              }}>
                {selectedWorkstation.station_id}
              </div>
              {selectedWorkstation.station_name}
              {selectedWorkstation.station_type && (
                <span className={`badge ${getStationTypeBadgeClass(selectedWorkstation.station_type)}`}>
                  {selectedWorkstation.station_type}
                </span>
              )}
            </h3>
            <button className="close-btn" onClick={() => setSelectedWorkstation(null)}>
              <X size={18} />
            </button>
          </div>
          <div className="detail-grid">
            <div className="detail-item">
              <div className="detail-item-label">Total Occupancy Time</div>
              <div className="detail-item-value">{formatTime(selectedWorkstation.occupancy_time_minutes)}</div>
            </div>
            <div className="detail-item">
              <div className="detail-item-label">Working Time</div>
              <div className="detail-item-value">{formatTime(selectedWorkstation.working_time_minutes)}</div>
            </div>
            <div className="detail-item">
              <div className="detail-item-label">Idle Time</div>
              <div className="detail-item-value">{formatTime(selectedWorkstation.idle_time_minutes)}</div>
            </div>
            <div className="detail-item">
              <div className="detail-item-label">Utilization Rate</div>
              <div className="detail-item-value">{selectedWorkstation.utilization_percentage.toFixed(1)}%</div>
            </div>
            <div className="detail-item">
              <div className="detail-item-label">Units Produced</div>
              <div className="detail-item-value">{formatNumber(selectedWorkstation.total_units_produced)}</div>
            </div>
            <div className="detail-item">
              <div className="detail-item-label">Throughput Rate</div>
              <div className="detail-item-value">{selectedWorkstation.throughput_rate.toFixed(1)}/hr</div>
            </div>
            <div className="detail-item">
              <div className="detail-item-label">Total Events</div>
              <div className="detail-item-value">{formatNumber(selectedWorkstation.event_count)}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;


