import type { PageResult } from './project'
import http from './request'

export interface AdminUser {
  id: number
  email: string
  name: string
  is_admin: boolean
  status: string
  created_at: string
}

export interface AdminProject {
  id: number
  name: string
  url: string
  creator_id: number
  model_config_id: number | null
  plan_status: string
  created_at: string
}

export interface PlatformSetting {
  id: number
  total_concurrency: number
  global_stress_limit: number
  new_user_stress_limit: number
  default_explore_minutes: number
  default_explore_pages: number
  retention_days: number
  stress_duration_seconds: number
  account_limit: number
  default_account_stress_limit: number
  disclaimer: string | null
  updated_at: string
}

export function listAdminUsers(params?: { status?: string; page?: number; page_size?: number }) {
  return http.get<PageResult<AdminUser>>('/admin/users', params)
}

export function updateAdminUser(id: number, data: { status?: string; reset_password?: string }) {
  return http.patch<AdminUser>(`/admin/users/${id}`, data)
}

export function deleteAdminUser(id: number) {
  return http.delete<null>(`/admin/users/${id}`)
}

export function listAdminProjects(params?: { page?: number; page_size?: number }) {
  return http.get<PageResult<AdminProject>>('/admin/projects', params)
}

export function deleteAdminProject(id: number) {
  return http.delete<null>(`/admin/projects/${id}`)
}

export function getPlatformSetting() {
  return http.get<PlatformSetting>('/admin/settings')
}

export function updatePlatformSetting(data: Partial<PlatformSetting>) {
  return http.patch<PlatformSetting>('/admin/settings', data)
}
