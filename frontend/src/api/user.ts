import type { UserInfo } from './auth'
import http from './request'

export function getMe() {
  return http.get<UserInfo>('/users/me')
}

export function updateMe(name: string) {
  return http.patch<UserInfo>('/users/me', { name })
}

export function changePassword(old_password: string, new_password: string) {
  return http.patch<null>('/users/me/password', { old_password, new_password })
}

export function requestCancel() {
  return http.post<null>('/users/me/cancel')
}

export function revokeCancel() {
  return http.post<null>('/users/me/cancel/revoke')
}
