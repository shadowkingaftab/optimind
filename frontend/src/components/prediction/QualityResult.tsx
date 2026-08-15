import React from 'react'
import Card from '../common/Card'
import ImageQualityNotice from '../upload/ImageQualityNotice'

interface QualityResultProps {
  score: number
  issues?: string[]
  recommendations?: string[]
}

const QualityResult: React.FC<QualityResultProps> = ({
  score,
  issues = [],
  recommendations = []
}) => {
  const quality = score >= 80 ? 'high' : score >= 50 ? 'medium' : 'low'

  return (
    <Card className="space-y-4">
      <h3 className="text-lg font-medium text-gray-900">Image Quality</h3>
      <ImageQualityNotice quality={quality} />
      {issues.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-gray-700">Issues Detected</h4>
          <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
            {issues.map((issue, index) => (
              <li key={index}>{issue}</li>
            ))}
          </ul>
        </div>
      )}
      {recommendations.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-gray-700">Recommendations</h4>
          <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
            {recommendations.map((rec, index) => (
              <li key={index}>{rec}</li>
            ))}
          </ul>
        </div>
      )}
    </Card>
  )
}

export default QualityResult
