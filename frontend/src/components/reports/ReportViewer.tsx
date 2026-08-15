import React from 'react'
import Card from '../common/Card'
import ReportHeader from './ReportHeader'
import ReportFindings from './ReportFindings'
import ReportDisclaimer from './ReportDisclaimer'

interface ReportData {
  id: string
  patientName?: string
  createdAt: string
  findings: Array<{
    condition: string
    description: string
    severity: 'mild' | 'moderate' | 'severe'
    recommendation: string
  }>
  summary: string
}

interface ReportViewerProps {
  report: ReportData
  onDownload?: () => void
}

const ReportViewer: React.FC<ReportViewerProps> = ({ report, onDownload }) => {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <Card>
        <ReportHeader
          patientName={report.patientName}
          reportId={report.id}
          createdAt={report.createdAt}
        />
        <ReportDownloadButton onDownload={onDownload} />
      </Card>

      <Card>
        <ReportFindings findings={report.findings} />
      </Card>

      <Card>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Summary</h3>
        <p className="text-gray-700">{report.summary}</p>
      </Card>

      <ReportDisclaimer />
    </div>
  )
}

export default ReportViewer
