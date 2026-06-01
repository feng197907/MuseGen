import axios from 'axios'
import { API_BASE_URL } from '../utils/constants'
import type { ApiResponse } from '../types/task'

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30_000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor: attach auth token (reserved for JWT)
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor: unwrap ApiResponse envelope
client.interceptors.response.use(
  (response) => {
    const wrapped: ApiResponse = response.data
    if (wrapped.code !== 0) {
      const err = new Error(wrapped.message || 'API error')
      ;(err as any).code = wrapped.code
      return Promise.reject(err)
    }
    return { ...response, data: wrapped.data }
  },
  (error) => {
    if (error.response) {
      const data = error.response.data
      const message = data?.message || data?.detail || error.message
      const err = new Error(message)
      ;(err as any).status = error.response.status
      return Promise.reject(err)
    }
    return Promise.reject(error)
  },
)

export default client
