import http from './request'

export interface UsageOverview {
  input_tokens: number
  output_tokens: number
  total_cost: number
  cost_unknown: boolean
  project_count: number
}

export interface UsageGroup {
  input_tokens: number
  output_tokens: number
  cost: number | null
  cost_unknown?: boolean
  project_id?: number
  project_name?: string
  model?: string
  task_type?: string
  task_id?: number
  name?: string
}

export interface UsageResult {
  overview: UsageOverview
  by_project: UsageGroup[]
  by_model: UsageGroup[]
  by_task: UsageGroup[]
}

export function getUsage(params?: { project_id?: number; days?: number }) {
  return http.get<UsageResult>('/usage', params)
}
