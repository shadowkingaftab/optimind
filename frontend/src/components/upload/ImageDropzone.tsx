import React, { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'

interface ImageDropzoneProps {
  onDrop: (files: File[]) => void
  accept?: Record<string, string[]>
  maxFiles?: number
  maxSize?: number
  disabled?: boolean
  className?: string
}

const ImageDropzone: React.FC<ImageDropzoneProps> = ({
  onDrop,
  accept,
  maxFiles = 1,
  maxSize = 10 * 1024 * 1024,
  disabled = false,
  className = ''
}) => {
  const handleDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      onDrop(acceptedFiles)
    }
  }, [onDrop])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: handleDrop,
    accept,
    maxFiles,
    maxSize,
    disabled
  })

  return (
    <div
      {...getRootProps()}
      className={`
        border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors
        ${isDragActive ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300 hover:border-gray-400'}
        ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
        ${className}
      `}
    >
      <input {...getInputProps()} disabled={disabled} />
      {isDragActive ? (
        <p className="text-sm text-indigo-600">Drop the image here...</p>
      ) : (
        <p className="text-sm text-gray-600">
          <span className="font-medium text-indigo-600">Upload</span> or drag and drop
        </p>
      )}
    </div>
  )
}

export default ImageDropzone
