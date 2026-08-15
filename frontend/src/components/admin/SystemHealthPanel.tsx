import React from 'react'
import Card from '../common/Card'
import Badge from '../common/Badge'

interface HealthMetric {
  name: string
  status: 'healthy' | 'degraded' | 'down'
  uptime?: string
  lastChecked: string
}

interface SystemHealthPanelProps {
  metrics: HealthMetric[]
}

const SystemHealthPanel: React.FC<SystemHealthPanelProps> = ({ metrics }) => {
  const statusColors = {
    healthy: 'success' as const,
    degraded: 'warning' as const,
    down: 'danger' as const
  }

  return (
    <Card>
      <h3 className="text-lg font-medium text-gray-900 mb-4">System Health</h3>
      <div className="space-y-4">
        {metrics.map((metric, index) => (
          <div key={index} className="flex items-center justify-between py-3 border-b border-gray-100 last:border-0">
            <div className="flex-1">
              <p className="font-medium text-gray-900">{metric.name}</p>
              <p className="text-sm text-gray-500">
                Last checked: {new Date(metric.lastChecked).toLocaleString()}
              </p>
            </div>
            <div className="text-right">
              <Badge variant={statusColors[metric.status]} size="sm">
                {metric.status}
              </Badge>
              {metric.uptime && (
                <p className="text-xs text-gray-500 mt-1">Uptime: {metric.uptime}</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </Card>
  )
}

export default SystemHealthPanel
