import React from 'react'
import Card from '../common/Card'
import Alert from '../common/Alert'

interface UncertainResultProps {
  message: string
  suggestions?: string[]
}

const UncertainResult: React.FC<UncertainResultProps> = ({
  message,
  suggestions = []
}) => {
  return (
    <Card className="space-y-4">
      <Alert type="warning" message={message} />
      {suggestions.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-gray-700">Suggestions</h4>
          <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
            {suggestions.map((suggestion, index) => (
              <li key={index}>{suggestion}</li>
            ))}
          </ul>
        </div>
      )}
      <div className="pt-4 border-t">
        <p className="text-sm text-gray-500">
          For a more accurate diagnosis, please consult with an ophthalmologist.
        </p>
      </div>
    </Card>
  )
}

export default UncertainResult
