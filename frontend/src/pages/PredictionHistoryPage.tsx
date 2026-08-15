import React from 'react'
import { Link } from 'react-router-dom'
import PredictionList from '../components/prediction/PredictionList'
import Card from '../components/common/Card'
import Button from '../components/common/Button'

const mockPredictions = [
  { id: '1', createdAt: new Date().toISOString(), results: [{ condition: 'Healthy', confidence: 95 }] },
  { id: '2', createdAt: new Date(Date.now() - 86400000).toISOString(), results: [{ condition: 'Cataract', confidence: 78 }] },
  { id: '3', createdAt: new Date(Date.now() - 172800000).toISOString(), results: [{ condition: 'Healthy', confidence: 92 }] }
]

const PredictionHistoryPage: React.FC = () => {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Prediction History</h1>
        <Link to="/upload">
          <Button>New Analysis</Button>
        </Link>
      </div>
      <PredictionList predictions={mockPredictions} />
    </div>
  )
}

export default PredictionHistoryPage
