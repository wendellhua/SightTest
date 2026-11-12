import http from './request'

export interface CaseStats {
  total: number
  pass: number
  fail: number
  blocked: number
  none: number
}

export interface ProjectDashboard {
  plan_status: string
  active_discovery: boolean
  run_status: string
  case_stats: Record<string, CaseStats>
  issue_stats: { open: number; misreported: number }
  running_tasks: { id: number; name: string; progress: number }[]
}

export function getProjectDashboard(projectId: number) {
  return http.get<ProjectDashboard>(`/projects/${projectId}/dashboard`)
}

export function getPlatformHome() {
  return http.get<{ project_count: number }>('/dashboard')
}
