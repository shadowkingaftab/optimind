import { useState, useEffect, useCallback } from 'react'

export function usePrediction(predictionId?: string) {
  const [prediction, setPrediction] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchPrediction = useCallback(async (id: string) => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`/api/predictions/${id}`)
      if (!response.ok) throw new Error('Prediction not found')
      const data = await response.json()
      setPrediction(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch prediction')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    if (predictionId) fetchPrediction(predictionId)
  }, [predictionId, fetchPrediction])

  const submitForAnalysis = useCallback(async (imageId: string) => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch('/api/predictions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ imageId })
      })
      if (!response.ok) throw new Error('Prediction failed')
      const data = await response.json()
      setPrediction(data)
      return data
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Prediction failed')
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  return { prediction, loading, error, fetchPrediction, submitForAnalysis }
}
