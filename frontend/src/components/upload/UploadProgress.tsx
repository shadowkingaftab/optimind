import React from 'react'

interface UploadProgressProps {
  progress: number
  status?: 'uploading' | 'processing' | 'complete' | 'error'
  message?: string
}

const UploadProgress: React.FC<UploadProgressProps> = ({
  progress,
  status = 'uploading',
  message
}) => {
  const statusConfig = {
    uploading: { color: 'bg-indigo-600', text: 'Uploading...' },
    processing: { color: 'bg-yellow-600', text: 'Processing...' },
    complete: { color: 'bg-green-600', text: 'Complete!' },
    error: { color: 'bg-red-600', text: 'Error' }
  }

  const config = statusConfig[status]

  return (
    <div className="space-y-2">
      <div className="flex justify-between text-sm">
        <span className="text-gray-700">{message || config.text}</span>
        <span className="text-gray-500">{Math.round(progress)}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2.5">
        <div
          className={`${config.color} h-2.5 rounded-full transition-all duration-300`}
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  )
}

export default UploadProgress
