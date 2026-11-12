import http from './request'

export interface Build {
  build_id: number
  project_id: number
  status: string
  stage: string | null
  progress: number
  message: string | null
  plan_incomplete: boolean
}

export interface PlanVersion {
  id: number
  project_id: number
  version_no: number
  status: string
  plan_incomplete: boolean
  explore_stats: Record<string, unknown> | null
  started_at: string
  completed_at: string | null
  created_at: string
}

export function startBuild(projectId: number, versionId?: number) {
  return http.post<{ build_id: number }>(`/projects/${projectId}/builds`, { version_id: versionId ?? null })
}

export function getBuild(projectId: number, buildId: number) {
  return http.get<Build>(`/projects/${projectId}/builds/${buildId}`)
}

export function terminateBuild(projectId: number, buildId: number) {
  return http.post<null>(`/projects/${projectId}/builds/${buildId}/terminate`)
}

export function listVersions(projectId: number) {
  return http.get<PlanVersion[]>(`/projects/${projectId}/versions`)
}
