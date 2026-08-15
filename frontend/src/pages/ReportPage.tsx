import React from 'react'
import { useParams } from 'react-router-dom'
import ReportViewer from '../components/reports/ReportViewer'

const mockReport = {
  id: 'RPT-001',
  patientName: 'John Doe',
  createdAt: new Date().toISOString(),
  summary: 'The analysis shows no significant abnormalities. The patient appears to have healthy eyes with normal retinal structure.',
  findings: [
    {
      condition: 'Normal Retina',
      description: 'Retina appears healthy with no signs of degeneration.',
      severity: 'mild' as const,
      recommendation: 'No action required. Continue regular checkups.'
    }
  ]
}

const ReportPage: React.FC = () => {
  const { id } = useParams<{ id: string }>()

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <ReportViewer report={mockReport} />
    </div>
  )
}

export default ReportPage
