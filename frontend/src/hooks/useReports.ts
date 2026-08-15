import { useState, useEffect, useCallback } from 'react'

export function useReports(reportId?: string) {
  const [reports, setReports] = useState<any[]>([])
  const [currentReport, setCurrentReport] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchReports = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch('/api/reports')
      if (!response.ok) throw new Error('Failed to fetch reports')
      const data = await response.json()
      setReports(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch reports')
    } finally {
      setLoading(false)
    }
  }, [])

  const fetchReport = useCallback(async (id: string) => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`/api/reports/${id}`)
      if (!response.ok) throw new Error('Report not found')
      const data = await response.json()
      setCurrentReport(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch report')
    } finally {
      setLoading(false)
    }
  }, [])

  const downloadReport = useCallback(async (id: string) => {
    const response = await fetch(`/api/reports/${id}/download`)
    if (!response.ok) throw new Error('Download failed')
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `report-${id}.pdf`
    link.click()
    window.URL.revokeObjectURL(url)
  }, [])

  useEffect(() => {
    if (reportId) fetchReport(reportId)
  }, [reportId, fetchReport])

  return { reports, currentReport, loading, error, fetchReports, fetchReport, downloadReport }
}
