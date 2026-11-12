import type { PageResult } from './project'
import http from './request'

export interface Report {
  id: number
  project_id: number
  scope: string
  execution_id: number | null
  status: string
  score: number
  risk_level: string
  top_issues: Record<string, unknown>[] | null
  summary: string | null
  content_ref: string | null
  created_at: string
}

export function createReport(projectId: number, data: { scope: string; execution_id?: number | null }) {
  return http.post<{ report_id: number }>(`/projects/${projectId}/reports`, data)
}

export function listReports(projectId: number, params?: { page?: number; page_size?: number }) {
  return http.get<PageResult<Report>>(`/projects/${projectId}/reports`, params)
}

export function getReport(projectId: number, reportId: number) {
  return http.get<Report>(`/projects/${projectId}/reports/${reportId}`)
}

export function downloadReportPdf(projectId: number, reportId: number) {
  return http.download(`/projects/${projectId}/reports/${reportId}/pdf`)
}
