import axios from 'axios'

// ─────────────────────────────────────────
// api.ts — Central Axios instance
//
// All API calls in the app go through this.
// Base URL is proxied by Vite → FastAPI :8000
// (see vite.config.ts → server.proxy)
// ─────────────────────────────────────────

const api = axios.create({
  baseURL: '/api/v1',       // matches main.py: prefix="/api/v1/..."
  timeout: 15_000,          // 15 second timeout
  headers: {
    'Content-Type': 'application/json',
  },
})

// ── Request interceptor ───────────────────
// Add auth headers here when you add JWT later

api.interceptors.request.use(
  (config) => {
    // Future: attach Bearer token
    // const token = localStorage.getItem('token')
    // if (token) config.headers.Authorization = `Bearer ${token}`
    return config
  },
  (error) => Promise.reject(error)
)

// ── Response interceptor ──────────────────
// Normalize errors into a consistent shape

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ||   // FastAPI validation error
      error.response?.data?.message ||
      error.message ||
      'An unexpected error occurred'

    // You can add global toast notifications here later
    console.error('[API Error]', message)

    return Promise.reject(new Error(message))
  }
)

export default api