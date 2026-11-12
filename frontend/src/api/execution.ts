import type { PageResult } from './project'
import http from './request'

export interface Execution {
  id: number
  project_id: number
  plan_version_id: number | null
  plan_version_no: number
  name: string
  scope: string
  is_debug: boolean
  status: string
  progress: number
  order_items: unknown[] | null
  summary: Record<string, unknown> | null
  started_at: string | null
  finished_at: string | null
  created_at: string
}

export interface CaseExecution {
  id: number
  case_id: number
  execution_id: number
  plan_version_id: number | null
  result: string
  evidence: Record<string, unknown> | null
  case_snapshot: Record<string, unknown> | null
  started_at: string | null
  finished_at: string | null
  created_at: string
}

export interface Issue {
  id: number
  project_id: number
  execution_id: number
  page: string
  severity: string
  description: string
  status: string
  screenshot_ref: string | null
  created_at: string
}

export interface MisreportPattern {
  id: number
  project_id: number
  page: string
  description: string
  status: string
  created_at: string
}

export function startExecution(projectId: number, data: { scope: string; case_ids?: number[] }) {
  return http.post<{ execution_id: number }>(`/projects/${projectId}/executions`, data)
}

export function listExecutions(
  projectId: number,
  params?: { include_debug?: boolean; page?: number; page_size?: number },
) {
  return http.get<PageResult<Execution>>(`/projects/${projectId}/executions`, params)
}

export function getExecution(projectId: number, executionId: number) {
  return http.get<Execution>(`/projects/${projectId}/executions/${executionId}`)
}

export function terminateExecution(projectId: number, executionId: number) {
  return http.post<null>(`/projects/${projectId}/executions/${executionId}/terminate`)
}

export function listCaseExecutions(projectId: number, executionId: number, result?: string) {
  return http.get<CaseExecution[]>(`/projects/${projectId}/executions/${executionId}/cases`, { result })
}

export function listIssues(projectId: number, params?: { severity?: string; page?: number; page_size?: number }) {
  return http.get<PageResult<Issue>>(`/projects/${projectId}/issues`, params)
}

export function updateIssue(projectId: number, issueId: number, status: string) {
  return http.patch<Issue>(`/projects/${projectId}/issues/${issueId}`, { status })
}

export function listMisreportPatterns(projectId: number) {
  return http.get<MisreportPattern[]>(`/projects/${projectId}/misreport-patterns`)
}

export function revokeMisreportPattern(projectId: number, patternId: number) {
  return http.patch<MisreportPattern>(`/projects/${projectId}/misreport-patterns/${patternId}`, {
    status: 'revoked',
  })
}
