import axios, { type AxiosInstance } from 'axios'
import { ElMessage } from 'element-plus'

/** 统一响应结构，对齐后端 `{code, message, data}`。 */
export interface ApiResponse<T = unknown> {
  code: number
  message: string
  data: T
}

const instance: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
})

instance.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

instance.interceptors.response.use(
  (response) => response,
  (error) => {
    const status: number | undefined = error.response?.status
    if (status === 401) {
      localStorage.removeItem('token')
      window.location.hash = '#/login'
    }
    const message: string = error.response?.data?.message ?? '网络错误，请稍后重试'
    ElMessage.error(message)
    return Promise.reject(error)
  },
)

/** 业务错误（HTTP 4xx/5xx）在拦截器中统一提示；成功响应返回 `ApiResponse`。 */
export const http = {
  get: <T>(url: string, params?: object) =>
    instance.get(url, { params }).then((r) => r.data as ApiResponse<T>),
  post: <T>(url: string, data?: unknown) =>
    instance.post(url, data).then((r) => r.data as ApiResponse<T>),
  patch: <T>(url: string, data?: unknown) =>
    instance.patch(url, data).then((r) => r.data as ApiResponse<T>),
  delete: <T>(url: string) =>
    instance.delete(url).then((r) => r.data as ApiResponse<T>),
  download: (url: string) => instance.get(url, { responseType: 'blob' }).then((r) => r.data as Blob),
}

export default http
