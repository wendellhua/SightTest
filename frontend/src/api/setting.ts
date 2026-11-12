import http from './request'

export interface UserSetting {
  explore_minutes: number
  explore_pages: number
  stress_limit: number
  account_stress_limit: number
}

export function getSetting() {
  return http.get<UserSetting>('/settings')
}

export function updateSetting(data: Partial<UserSetting>) {
  return http.patch<UserSetting>('/settings', data)
}
