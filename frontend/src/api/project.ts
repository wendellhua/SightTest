import http from './request'

export interface Project {
  id: number
  name: string
  url: string
  creator_id: number
  model_config_id: number | null
  plan_status: string
  plan_incomplete: boolean
  active_discovery: boolean
  created_at: string
  updated_at: string
}

export interface Account {
  id: number
  project_id: number
  username: string
  is_primary: boolean
  last_login_status: string | null
  last_login_fail_reason: string | null
  last_login_at: string | null
}

export interface PageResult<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

export interface AccountInput {
  username: string
  password: string
  is_primary: boolean
}

export function checkUrl(url: string) {
  return http.post<{ reachable: boolean }>('/projects/url-check', { url })
}

export function createProject(data: {
  name: string
  url: string
  model_config_id?: number | null
  accounts: AccountInput[]
}) {
  return http.post<Project>('/projects', data)
}

export function listProjects(page = 1, pageSize = 20) {
  return http.get<PageResult<Project>>('/projects', { page, page_size: pageSize })
}

export function getProject(id: number) {
  return http.get<Project>(`/projects/${id}`)
}

export function deleteProject(id: number) {
  return http.delete<null>(`/projects/${id}`)
}

export function listAccounts(projectId: number) {
  return http.get<Account[]>(`/projects/${projectId}/accounts`)
}
