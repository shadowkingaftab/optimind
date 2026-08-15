import { create } from 'zustand'
import { Report, ReportFilter } from '../types/report.types'

interface ReportState {
  reports: Report[]
  currentReport: Report | null
  filter: ReportFilter
  loading: boolean
  error: string | null
  setReports: (reports: Report[]) => void
  setCurrentReport: (report: Report | null) => void
  setFilter: (filter: ReportFilter) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  clearReports: () => void
}

export const useReportStore = create<ReportState>((set) => ({
  reports: [],
  currentReport: null,
  filter: {},
  loading: false,
  error: null,

  setReports: (reports) => set({ reports }),
  setCurrentReport: (currentReport) => set({ currentReport }),
  setFilter: (filter) => set({ filter }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  clearReports: () => set({ reports: [], currentReport: null })
}))
