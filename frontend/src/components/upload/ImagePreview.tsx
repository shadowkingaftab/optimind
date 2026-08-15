import React from 'react'

interface ImagePreviewProps {
  file: File
  onRemove?: () => void
  className?: string
}

const ImagePreview: React.FC<ImagePreviewProps> = ({
  file,
  onRemove,
  className = ''
}) => {
  const [preview, setPreview] = React.useState<string | null>(null)

  React.useEffect(() => {
    const reader = new FileReader()
    reader.onloadend = () => {
      setPreview(reader.result as string)
    }
    reader.readAsDataURL(file)
    return () => {
      if (preview) URL.revokeObjectURL(preview)
    }
  }, [file])

  return (
    <div className={`relative rounded-lg overflow-hidden bg-gray-100 ${className}`}>
      <div className="aspect-video flex items-center justify-center">
        {preview ? (
          <img src={preview} alt="Preview" className="max-h-full max-w-full object-contain" />
        ) : (
          <div className="text-gray-400">Loading preview...</div>
        )}
      </div>
      <div className="absolute top-2 right-2 flex space-x-2">
        {onRemove && (
          <button
            onClick={onRemove}
            className="p-1 bg-red-600 text-white rounded-full hover:bg-red-700 focus:outline-none"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>
      <div className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-50 text-white text-xs p-2">
        {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
      </div>
    </div>
  )
}

export default ImagePreview
