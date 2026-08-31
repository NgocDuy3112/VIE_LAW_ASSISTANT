import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { LoginForm } from '../components/LoginForm'
import { RegisterForm } from '../components/RegisterForm'
import { useAuth } from '../hooks/useAuth'

export function AuthPage() {
  const [isLogin, setIsLogin] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { login, register } = useAuth()
  const navigate = useNavigate()

  const handleLogin = async (email: string, password: string) => {
    try {
      setError(null)
      await login(email, password)
      navigate('/chat')
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } }
      setError(axiosError.response?.data?.detail || 'Đăng nhập thất bại')
    }
  }

  const handleRegister = async (username: string, email: string, password: string) => {
    try {
      setError(null)
      await register(username, email, password)
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } }
      setError(axiosError.response?.data?.detail || 'Đăng ký thất bại')
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-container">
        <h1>VIE Law Assistant</h1>
        <p>Trợ lý pháp luật Việt Nam</p>
        {isLogin ? (
          <LoginForm
            onSubmit={handleLogin}
            onSwitchToRegister={() => setIsLogin(false)}
            error={error}
          />
        ) : (
          <RegisterForm
            onSubmit={handleRegister}
            onSwitchToLogin={() => setIsLogin(true)}
            error={error}
          />
        )}
      </div>
    </div>
  )
}
