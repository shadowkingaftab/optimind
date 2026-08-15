import { create } from 'zustand'
import { useAuthStore } from './auth-slice'
import { useUploadStore } from './upload-slice'
import { usePredictionStore } from './prediction-slice'
import { useReportStore } from './report-slice'

export const useStore = create<{
  auth: ReturnType<typeof useAuthStore>
  upload: ReturnType<typeof useUploadStore>
  prediction: ReturnType<typeof usePredictionStore>
  report: ReturnType<typeof useReportStore>
}>((set) => ({
  auth: useAuthStore(),
  upload: useUploadStore(),
  prediction: usePredictionStore(),
  report: useReportStore()
}))
