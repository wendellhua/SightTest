import http from './request'

export interface UserInfo {
  id: number
  email: string
  name: string
  is_admin: boolean
  status: string
  admin_password_changed: boolean
  created_at: string
}

export interface TokenResponse {
  token: string
  user: UserInfo
}

export function sendCode(email: string, purpose: 'register' | 'reset_password') {
  return http.post<null>('/auth/send-code', { email, purpose })
}

export function register(data: { email: string; code: string; password: string; name: string }) {
  return http.post<TokenResponse>('/auth/register', data)
}

export function login(email: string, password: string) {
  return http.post<TokenResponse>('/auth/login', { email, password })
}

export function resetPassword(data: { email: string; code: string; new_password: string }) {
  return http.post<null>('/auth/reset-password', data)
}
