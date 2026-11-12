import http from './request'

export interface ModelConfig {
  id: number
  user_id: number
  name: string
  base_url: string
  model: string
  status: string
  created_at: string
  updated_at: string
}

export interface ModelCheckResult {
  ok: boolean
  supports_vision: boolean
  message: string
}

export function listModels() {
  return http.get<ModelConfig[]>('/models')
}

export function createModel(data: { name: string; base_url: string; api_key: string; model: string }) {
  return http.post<ModelConfig>('/models', data)
}

export function updateModel(
  id: number,
  data: { name?: string; base_url?: string; api_key?: string; model?: string },
) {
  return http.patch<ModelConfig>(`/models/${id}`, data)
}

export function deleteModel(id: number) {
  return http.delete<null>(`/models/${id}`)
}

export function testModel(id: number) {
  return http.post<ModelCheckResult>(`/models/${id}/test`)
}
