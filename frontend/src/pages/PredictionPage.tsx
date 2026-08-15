import React from 'react'
import { useParams } from 'react-router-dom'
import Card from '../components/common/Card'
import PredictionSummary from '../components/prediction/PredictionSummary'
import HeatmapViewer from '../components/prediction/HeatmapViewer'
import ModelInformation from '../components/prediction/ModelInformation'
import ConfidenceIndicator from '../components/prediction/ConfidenceIndicator'

interface PredictionResult {
  condition: string
  confidence: number
  riskLevel: 'low' | 'medium' | 'high'
}

const PredictionPage: React.FC = () => {
  const { id } = useParams<{ id: string }>()

  const results: PredictionResult[] = [
    { condition: 'Diabetic Retinopathy', confidence: 92, riskLevel: 'low' },
    { condition: 'Glaucoma', confidence: 15, riskLevel: 'low' }
  ]

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Prediction Results</h1>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <HeatmapViewer imageUrl="/placeholder-eye.jpg" heatmapUrl="/heatmap-overlay.png" />
          </Card>
          <PredictionSummary
            results={results}
            processingTime={1.2}
            modelVersion="v2.1.0"
            timestamp={new Date().toISOString()}
          />
        </div>
        <div className="space-y-6">
          <Card>
            <h3 className="text-lg font-medium text-gray-900 mb-4">Confidence</h3>
            <div className="space-y-4">
              {results.map((result, index) => (
                <ConfidenceIndicator key={index} value={result.confidence} label={result.condition} />
              ))}
            </div>
          </Card>
          <ModelInformation
            name="EyeDx Model"
            version="v2.1.0"
            accuracy={0.96}
            lastUpdated={new Date().toISOString()}
          />
        </div>
      </div>
    </div>
  )
}

export default PredictionPage
