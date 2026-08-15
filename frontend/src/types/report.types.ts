export interface Report {
  id: string
  predictionId: string
  userId: string
  patientName?: string
  createdAt: string
  summary: string
  findings: ReportFinding[]
  recommendations: string[]
  disclaimer: string
}

export interface ReportFinding {
  condition: string
  description: string
  severity: 'mild' | 'moderate' | 'severe'
  recommendation: string
}

export interface ReportFilter {
  startDate?: string
  endDate?: string
  predictionId?: string
}
