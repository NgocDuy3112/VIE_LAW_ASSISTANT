import axios from 'axios'

const authApi = axios.create({
  baseURL: '/api/auth',
})

const chatApi = axios.create({
  baseURL: '/api/chat',
})

// Add auth token to requests
chatApi.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle 401 errors
chatApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const auth = {
  register: (data: { username: string; email: string; password: string }) =>
    authApi.post('/register', data),
  login: (data: { email: string; password: string }) =>
    authApi.post('/login', data),
  refresh: (data: { refresh_token: string }) =>
    authApi.post('/refresh', data),
  logout: (data: { refresh_token: string }) =>
    authApi.post('/logout', data),
}

export const chat = {
  sendMessage: (messages: { role: string; content: string; session_id?: string }[]) =>
    chatApi.post('/v1/response', messages),
  getSessions: () =>
    chatApi.get('/v1/sessions'),
  getMessages: (sessionId: string) =>
    chatApi.get(`/v1/sessions/${sessionId}/messages`),
  deleteSession: (sessionId: string) =>
    chatApi.delete(`/v1/sessions/${sessionId}`),
}

export default { auth, chat }
