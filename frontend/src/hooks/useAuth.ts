import { useState, useEffect } from 'react'
import { auth } from '../services/api'

export function useAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    setIsAuthenticated(!!token)
    setIsLoading(false)
  }, [])

  const login = async (email: string, password: string) => {
    const response = await auth.login({ email, password })
    localStorage.setItem('access_token', response.data.access_token)
    localStorage.setItem('refresh_token', response.data.refresh_token)
    setIsAuthenticated(true)
    return response.data
  }

  const register = async (username: string, email: string, password: string) => {
    await auth.register({ username, email, password })
  }

  const logout = async () => {
    const refreshToken = localStorage.getItem('refresh_token')
    if (refreshToken) {
      try {
        await auth.logout({ refresh_token: refreshToken })
      } catch {
        // Ignore logout errors
      }
    }
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setIsAuthenticated(false)
  }

  return { isAuthenticated, isLoading, login, register, logout }
}
