import React from 'react'

interface ReportHeaderProps {
  reportId: string
  patientName?: string
  createdAt: string
  doctorName?: string
}

const ReportHeader: React.FC<ReportHeaderProps> = ({
  reportId,
  patientName,
  createdAt,
  doctorName
}) => {
  return (
    <div className="border-b border-gray-200 pb-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Eye Examination Report</h1>
          <p className="mt-1 text-sm text-gray-500">Report ID: {reportId}</p>
        </div>
        <div className="text-right text-sm text-gray-500">
          <p>{new Date(createdAt).toLocaleDateString()}</p>
          <p>{new Date(createdAt).toLocaleTimeString()}</p>
        </div>
      </div>
      {(patientName || doctorName) && (
        <div className="mt-4 grid grid-cols-2 gap-4">
          {patientName && (
            <div>
              <p className="text-sm font-medium text-gray-700">Patient</p>
              <p className="text-sm text-gray-900">{patientName}</p>
            </div>
          )}
          {doctorName && (
            <div>
              <p className="text-sm font-medium text-gray-700">Physician</p>
              <p className="text-sm text-gray-900">{doctorName}</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default ReportHeader
