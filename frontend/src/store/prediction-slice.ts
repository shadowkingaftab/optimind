import { create } from 'zustand'
import { Prediction, PredictionFilter } from '../types/prediction.types'

interface PredictionState {
  predictions: Prediction[]
  currentPrediction: Prediction | null
  filter: PredictionFilter
  loading: boolean
  error: string | null
  setPredictions: (predictions: Prediction[]) => void
  setCurrentPrediction: (prediction: Prediction | null) => void
  setFilter: (filter: PredictionFilter) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  clearPredictions: () => void
}

export const usePredictionStore = create<PredictionState>((set) => ({
  predictions: [],
  currentPrediction: null,
  filter: {},
  loading: false,
  error: null,

  setPredictions: (predictions) => set({ predictions }),
  setCurrentPrediction: (currentPrediction) => set({ currentPrediction }),
  setFilter: (filter) => set({ filter }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  clearPredictions: () => set({ predictions: [], currentPrediction: null })
}))
