import React from 'react'

interface ConfidenceIndicatorProps {
  value: number
  label?: string
  showLabel?: boolean
}

const ConfidenceIndicator: React.FC<ConfidenceIndicatorProps> = ({
  value,
  label = 'Confidence',
  showLabel = true
}) => {
  const getColor = (val: number) => {
    if (val >= 80) return 'bg-green-500'
    if (val >= 60) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  return (
    <div className="w-full">
      {showLabel && (
        <div className="flex justify-between text-sm mb-1">
          <span className="text-gray-700">{label}</span>
          <span className="text-gray-900 font-medium">{value}%</span>
        </div>
      )}
      <div className="w-full bg-gray-200 rounded-full h-2.5">
        <div
          className={`${getColor(value)} h-2.5 rounded-full transition-all duration-500`}
          style={{ width: `${value}%` }}
        />
      </div>
    </div>
  )
}

export default ConfidenceIndicator
