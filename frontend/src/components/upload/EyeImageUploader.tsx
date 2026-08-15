import React, { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import Button from '../../common/Button'
import ImagePreview from './ImagePreview'
import ImageRequirements from './ImageRequirements'

interface EyeImageUploaderProps {
  onUpload?: (files: File[]) => Promise<void>
  maxFiles?: number
  accept?: string[]
}

const EyeImageUploader: React.FC<EyeImageUploaderProps> = ({
  onUpload,
  maxFiles = 1,
  accept = ['image/jpeg', 'image/png', 'image/dicom']
}) => {
  const [files, setFiles] = React.useState<File[]>([])
  const [uploading, setUploading] = React.useState(false)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles(acceptedFiles.slice(0, maxFiles))
  }, [maxFiles])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: accept.reduce((acc, type) => ({ ...acc, [type]: [] }), {}),
    maxFiles
  })

  const handleUpload = async () => {
    if (!files.length || !onUpload) return
    setUploading(true)
    try {
      await onUpload(files)
    } finally {
      setUploading(false)
    }
  }

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index))
  }

  return (
    <div className="space-y-6">
      <ImageRequirements />

      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300 hover:border-gray-400'
        }`}
      >
        <input {...getInputProps()} />
        <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
        <p className="mt-2 text-sm text-gray-600">
          {isDragActive ? (
            'Drop the image here...'
          ) : (
            <>
              <span className="font-medium text-indigo-600 hover:text-indigo-500">Upload a file</span>
              {' or drag and drop'}
            </>
          )}
        </p>
        <p className="mt-1 text-xs text-gray-500">PNG, JPG up to 10MB</p>
      </div>

      {files.length > 0 && (
        <div className="space-y-4">
          {files.map((file, index) => (
            <ImagePreview key={index} file={file} onRemove={() => removeFile(index)} />
          ))}
          <Button onClick={handleUpload} loading={uploading} className="w-full">
            Upload and Analyze
          </Button>
        </div>
      )}
    </div>
  )
}

export default EyeImageUploader
