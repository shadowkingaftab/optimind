import React from 'react'
import Card from '../common/Card'
import Badge from '../common/Badge'

interface PredictionCardProps {
  id: string
  condition: string
  confidence: number
  riskLevel: 'low' | 'medium' | 'high'
  timestamp: string
  onClick?: () => void
}

const PredictionCard: React.FC<PredictionCardProps> = ({
  id,
  condition,
  confidence,
  riskLevel,
  timestamp,
  onClick
}) => {
  return (
    <Card className="hover:shadow-md transition-shadow cursor-pointer" onClick={onClick}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-2">
            <h4 className="font-medium text-gray-900">{condition}</h4>
            <Badge
              variant={
                riskLevel === 'high'
                  ? 'danger'
                  : riskLevel === 'medium'
                  ? 'warning'
                  : 'primary'
              }
              size="sm"
            >
              {riskLevel}
            </Badge>
          </div>
          <div className="mt-2 flex items-center space-x-4">
            <span className="text-sm text-gray-500">
              {new Date(timestamp).toLocaleDateString()}
            </span>
          </div>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-indigo-600">{confidence}%</div>
          <div className="text-xs text-gray-500">confidence</div>
        </div>
      </div>
    </Card>
  )
}

export default PredictionCard
