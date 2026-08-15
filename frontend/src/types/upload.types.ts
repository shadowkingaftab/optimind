export interface UploadedFile {
  id: string
  file: File
  preview: string
  status: 'pending' | 'uploading' | 'processing' | 'complete' | 'error'
  progress: number
  result?: UploadResult
  error?: string
}

export interface UploadResult {
  predictionId: string
  qualityScore: number
  message: string
}

export interface UploadValidationError {
  field: string
  message: string
}
