import React from 'react'
import Badge from '../common/Badge'

interface Finding {
  condition: string
  description: string
  severity: 'mild' | 'moderate' | 'severe'
  recommendation: string
}

interface ReportFindingsProps {
  findings: Finding[]
}

const severityColors = {
  mild: 'success' as const,
  moderate: 'warning' as const,
  severe: 'danger' as const
}

const ReportFindings: React.FC<ReportFindingsProps> = ({ findings }) => {
  return (
    <div>
      <h3 className="text-lg font-medium text-gray-900 mb-4">Findings</h3>
      <div className="space-y-6">
        {findings.map((finding, index) => (
          <div key={index} className="border-b border-gray-100 last:border-0 pb-6 last:pb-0">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <h4 className="font-medium text-gray-900">{finding.condition}</h4>
                  <Badge variant={severityColors[finding.severity]} size="sm">
                    {finding.severity}
                  </Badge>
                </div>
                <p className="mt-1 text-sm text-gray-600">{finding.description}</p>
                <div className="mt-2">
                  <p className="text-sm font-medium text-gray-700">Recommendation:</p>
                  <p className="text-sm text-gray-600">{finding.recommendation}</p>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default ReportFindings
