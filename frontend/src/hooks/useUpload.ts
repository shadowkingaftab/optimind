import { useState, useCallback } from 'react'

export function useUpload() {
  const [files, setFiles] = useState<File[]>([])
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)

  const handleDrop = useCallback((acceptedFiles: File[]) => {
    setFiles(acceptedFiles)
  }, [])

  const upload = useCallback(async () => {
    if (!files.length) return
    setUploading(true)
    setProgress(0)
    const formData = new FormData()
    files.forEach((file) => formData.append('files', file))
    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      })
      if (!response.ok) throw new Error('Upload failed')
      setProgress(100)
    } finally {
      setUploading(false)
    }
  }, [files])

  const reset = useCallback(() => {
    setFiles([])
    setProgress(0)
  }, [])

  return { files, uploading, progress, handleDrop, upload, reset }
}
