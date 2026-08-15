import React from 'react'
import Card from '../common/Card'
import Badge from '../common/Badge'

interface PredictionResult {
  condition: string
  confidence: number
  riskLevel: 'low' | 'medium' | 'high'
}

interface PredictionSummaryProps {
  results: PredictionResult[]
  processingTime?: number
  modelVersion?: string
  timestamp?: string
}

const PredictionSummary: React.FC<PredictionSummaryProps> = ({
  results,
  processingTime,
  modelVersion,
  timestamp
}) => {
  return (
    <Card className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium text-gray-900">Analysis Summary</h3>
        {timestamp && (
          <span className="text-sm text-gray-500">{new Date(timestamp).toLocaleString()}</span>
        )}
      </div>

      <div className="space-y-4">
        {results.map((result, index) => (
          <div key={index} className="flex items-center justify-between py-3 border-b border-gray-100 last:border-0">
            <div>
              <p className="font-medium text-gray-900">{result.condition}</p>
              <p className="text-sm text-gray-500">{result.confidence}% confidence</p>
            </div>
            <Badge
              variant={
                result.riskLevel === 'high'
                  ? 'danger'
                  : result.riskLevel === 'medium'
                  ? 'warning'
                  : 'primary'
              }
            >
              {result.riskLevel} risk
            </Badge>
          </div>
        ))}
      </div>

      <div className="flex items-center justify-between text-sm text-gray-500 pt-4 border-t">
        <span>Model: {modelVersion || 'v1.0'}</span>
        {processingTime && <span>Processed in {processingTime}s</span>}
      </div>
    </Card>
  )
}

export default PredictionSummary
