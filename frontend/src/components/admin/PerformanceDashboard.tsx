import React from 'react'
import Card from '../common/Card'

interface MetricCardProps {
  title: string
  value: string | number
  change?: number
  unit?: string
}

const MetricCard: React.FC<MetricCardProps> = ({ title, value, change, unit }) => {
  return (
    <Card padding="md">
      <p className="text-sm font-medium text-gray-600">{title}</p>
      <p className="mt-2 text-3xl font-bold text-gray-900">
        {value}
        {unit && <span className="text-lg text-gray-500 ml-1">{unit}</span>}
      </p>
      {change !== undefined && (
        <p className={`mt-2 text-sm ${change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
          {change >= 0 ? '+' : ''}{change}%
        </p>
      )}
    </Card>
  )
}

interface PerformanceData {
  timestamp: string
  value: number
}

interface PerformanceDashboardProps {
  metrics: Array<{
    title: string
    value: string | number
    unit?: string
    change?: number
  }>
  charts?: Array<{
    title: string
    data: PerformanceData[]
  }>
}

const PerformanceDashboard: React.FC<PerformanceDashboardProps> = ({ metrics, charts }) => {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {metrics.map((metric, index) => (
          <MetricCard key={index} {...metric} />
        ))}
      </div>

      {charts && (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {charts.map((chart, index) => (
            <Card key={index}>
              <h3 className="text-lg font-medium text-gray-900 mb-4">{chart.title}</h3>
              <div className="h-64 flex items-center justify-center text-gray-400">
                <svg className="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}

export default PerformanceDashboard
