import React from 'react'
import Card from '../common/Card'

interface ModelInformationProps {
  name: string
  version: string
  accuracy?: number
  lastUpdated?: string
  description?: string
}

const ModelInformation: React.FC<ModelInformationProps> = ({
  name,
  version,
  accuracy,
  lastUpdated,
  description
}) => {
  return (
    <Card className="space-y-4">
      <h3 className="text-lg font-medium text-gray-900">Model Information</h3>
      <div className="space-y-3">
        <div className="flex justify-between">
          <span className="text-gray-600">Model</span>
          <span className="font-medium text-gray-900">{name}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-600">Version</span>
          <span className="font-medium text-gray-900">{version}</span>
        </div>
        {accuracy && (
          <div className="flex justify-between">
            <span className="text-gray-600">Accuracy</span>
            <span className="font-medium text-gray-900">{(accuracy * 100).toFixed(1)}%</span>
          </div>
        )}
        {lastUpdated && (
          <div className="flex justify-between">
            <span className="text-gray-600">Last Updated</span>
            <span className="font-medium text-gray-900">
              {new Date(lastUpdated).toLocaleDateString()}
            </span>
          </div>
        )}
        {description && (
          <div className="pt-3 border-t">
            <p className="text-sm text-gray-600">{description}</p>
          </div>
        )}
      </div>
    </Card>
  )
}

export default ModelInformation
