export function formatConfidence(value: number): string {
  return `${value.toFixed(1)}%`
}

export function getConfidenceColor(value: number): string {
  if (value >= 80) return 'text-green-600'
  if (value >= 60) return 'text-yellow-600'
  return 'text-red-600'
}

export function getConfidenceLabel(value: number): string {
  if (value >= 80) return 'High'
  if (value >= 60) return 'Medium'
  return 'Low'
}
