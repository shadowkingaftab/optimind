export interface ModelVersion {
  id: string
  name: string
  version: string
  status: 'active' | 'staging' | 'deprecated'
  accuracy: number
  deployedAt: string
  description?: string
}

export interface ModelHealth {
  name: string
  status: 'healthy' | 'degraded' | 'down'
  uptime?: string
  lastChecked: string
}

export interface ModelPerformanceMetrics {
  totalPredictions: number
  averageLatency: number
  errorRate: number
  throughput: number
}
