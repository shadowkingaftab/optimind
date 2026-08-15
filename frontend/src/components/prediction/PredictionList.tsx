import React from 'react'
import { Link } from 'react-router-dom'
import Card from '../common/Card'
import EmptyState from '../common/EmptyState'

interface PredictionItem {
  id: string
  createdAt: string
  results: Array<{ condition: string; confidence: number }>
}

interface PredictionListProps {
  predictions: PredictionItem[]
  isLoading?: boolean
}

const PredictionList: React.FC<PredictionListProps> = ({ predictions, isLoading }) => {
  if (isLoading) {
    return (
      <Card>
        <div className="animate-pulse space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-24 bg-gray-100 rounded" />
          ))}
        </div>
      </Card>
    )
  }

  if (predictions.length === 0) {
    return (
      <EmptyState
        icon={
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7z" />
            <circle cx="12" cy="12" r="3" />
          </svg>
        }
        title="No predictions yet"
        description="Upload an eye image to get started"
        action={
          <Link to="/upload">
            <button className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700">
              Upload Image
            </button>
          </Link>
        }
      />
    )
  }

  return (
    <div className="space-y-4">
      {predictions.map((prediction) => (
        <Card key={prediction.id} className="hover:shadow-md transition-shadow">
          <Link to={`/predictions/${prediction.id}`} className="block">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-gray-900">
                  {prediction.results[0]?.condition || 'Analysis'}
                </p>
                <p className="text-sm text-gray-500">
                  {new Date(prediction.createdAt).toLocaleDateString()}
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm font-medium text-indigo-600">
                  {prediction.results[0]?.confidence}%
                </p>
                <p className="text-xs text-gray-500">confidence</p>
              </div>
            </div>
          </Link>
        </Card>
      ))}
    </div>
  )
}

export default PredictionList
