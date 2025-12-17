// API configuration using environment variables
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'

export const apiConfig = {
  baseUrl: API_URL,
  wsUrl: WS_URL,
  endpoints: {
    reports: `${API_URL}/api/v1/reports`,
    incidents: `${API_URL}/api/v1/incidents`,
    resources: `${API_URL}/api/v1/resources`,
    auth: {
      login: `${API_URL}/api/v1/auth/login`,
      register: `${API_URL}/api/v1/auth/register`,
      me: `${API_URL}/api/v1/auth/me`,
    },
    analytics: `${API_URL}/api/v1/analytics`,
  },
}

// Helper function to get auth token from localStorage
export const getAuthToken = (): string | null => {
  if (typeof window === 'undefined') return null
  return localStorage.getItem('auth_token')
}

// Helper function to set auth token
export const setAuthToken = (token: string): void => {
  if (typeof window === 'undefined') return
  localStorage.setItem('auth_token', token)
}

// Helper function to remove auth token
export const removeAuthToken = (): void => {
  if (typeof window === 'undefined') return
  localStorage.removeItem('auth_token')
}

// Fetch wrapper with authentication
export const apiFetch = async (
  url: string,
  options: RequestInit = {}
): Promise<Response> => {
  const token = getAuthToken()
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  }
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  
  return fetch(url, {
    ...options,
    headers,
  })
}

