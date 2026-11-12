import type { PageResult } from './project'
import http from './request'

export interface CaseItem {
  id: number
  project_id: number
  plan_version_id: number
  case_type: string
  module_path: string | null
  page: string | null
  name: string
  priority: string
  precondition: string | null
  steps: string
  expect: string
  automatable: boolean
  result: string
  remark: string | null
  flags: Record<string, unknown> | null
  extension: Record<string, unknown> | null
  created_at: string
  updated_at: string
}

export interface CaseInput {
  case_type: string
  module_path?: string | null
  page?: string | null
  name: string
  priority: string
  precondition?: string | null
  steps: string
  expect: string
  automatable: boolean
  remark?: string | null
  extension?: Record<string, unknown> | null
}

export function listCases(projectId: number, params?: { case_type?: string; page?: number; page_size?: number }) {
  return http.get<PageResult<CaseItem>>(`/projects/${projectId}/cases`, params)
}

export function createCase(projectId: number, data: CaseInput) {
  return http.post<CaseItem>(`/projects/${projectId}/cases`, data)
}

export function updateCase(projectId: number, caseId: number, data: Partial<CaseInput>) {
  return http.patch<CaseItem>(`/projects/${projectId}/cases/${caseId}`, data)
}

export function deleteCase(projectId: number, caseId: number) {
  return http.delete<null>(`/projects/${projectId}/cases/${caseId}`)
}

export function debugCase(projectId: number, caseId: number) {
  return http.post<{ execution_id: number }>(`/projects/${projectId}/cases/${caseId}/debug`)
}
