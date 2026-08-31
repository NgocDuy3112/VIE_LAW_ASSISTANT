import { useState } from 'react'

interface ChatInputProps {
  onSend: (message: string) => void
  isLoading: boolean
}

export function ChatInput({ onSend, isLoading }: ChatInputProps) {
  const [message, setMessage] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (message.trim() && !isLoading) {
      onSend(message.trim())
      setMessage('')
    }
  }

  return (
    <form className="chat-input" onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Nhập câu hỏi về luật pháp..."
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        disabled={isLoading}
      />
      <button type="submit" disabled={isLoading || !message.trim()}>
        {isLoading ? '...' : 'Gửi'}
      </button>
    </form>
  )
}
