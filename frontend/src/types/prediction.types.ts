export interface PredictionResult {
  condition: string
  confidence: number
  riskLevel: 'low' | 'medium' | 'high'
  description: string
}

export interface Prediction {
  id: string
  userId: string
  createdAt: string
  results: PredictionResult[]
  processingTime: number
  modelVersion: string
  imageUrl: string
  heatmapUrl?: string
}

export interface PredictionRequest {
  imageId: string
}

export interface PredictionFilter {
  startDate?: string
  endDate?: string
  riskLevel?: 'low' | 'medium' | 'high'
  condition?: string
}
