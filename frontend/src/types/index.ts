export interface User {
  id: string
  username: string
  email: string
}

export interface Session {
  id: string
  title: string | null
  created_at: string
}

export interface Message {
  id?: string
  role: 'user' | 'assistant' | 'system'
  content: string
  created_at?: string
  session_id?: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
}

export interface AuthResponse {
  access_token: string
  refresh_token: string
}

export interface ChatResponse {
  role: string
  content: string
  session_id: string
}
