import { useState } from 'react'

interface LoginFormProps {
  onSubmit: (email: string, password: string) => Promise<void>
  onSwitchToRegister: () => void
  error: string | null
}

export function LoginForm({ onSubmit, onSwitchToRegister, error }: LoginFormProps) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    try {
      await onSubmit(email, password)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="auth-form">
      <h2>Đăng nhập</h2>
      {error && <div className="error">{error}</div>}
      <form onSubmit={handleSubmit}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Mật khẩu"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Đang đăng nhập...' : 'Đăng nhập'}
        </button>
      </form>
      <p>
        Chưa có tài khoản?{' '}
        <button type="button" onClick={onSwitchToRegister}>
          Đăng ký
        </button>
      </p>
    </div>
  )
}
