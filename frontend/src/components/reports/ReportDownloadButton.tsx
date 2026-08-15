import React from 'react'

interface ReportDownloadButtonProps {
  onDownload?: () => void
  className?: string
}

const ReportDownloadButton: React.FC<ReportDownloadButtonProps> = ({
  onDownload,
  className = ''
}) => {
  const handleClick = () => {
    if (onDownload) {
      onDownload()
    } else {
      alert('Download functionality not implemented')
    }
  }

  return (
    <div className={`mt-6 flex justify-end ${className}`}>
      <button
        onClick={handleClick}
        className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
      >
        <svg className="mr-2 -ml-1 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
        </svg>
        Download Report
      </button>
    </div>
  )
}

export default ReportDownloadButton
