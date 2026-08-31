import { useState } from 'react'

interface RegisterFormProps {
  onSubmit: (username: string, email: string, password: string) => Promise<void>
  onSwitchToLogin: () => void
  error: string | null
}

export function RegisterForm({ onSubmit, onSwitchToLogin, error }: RegisterFormProps) {
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    try {
      await onSubmit(username, email, password)
      onSwitchToLogin()
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="auth-form">
      <h2>Đăng ký</h2>
      {error && <div className="error">{error}</div>}
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Tên người dùng"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
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
          {isLoading ? 'Đang đăng ký...' : 'Đăng ký'}
        </button>
      </form>
      <p>
        Đã có tài khoản?{' '}
        <button type="button" onClick={onSwitchToLogin}>
          Đăng nhập
        </button>
      </p>
    </div>
  )
}
