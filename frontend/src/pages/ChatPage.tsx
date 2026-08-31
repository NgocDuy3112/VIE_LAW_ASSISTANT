import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { chat } from '../services/api'
import { Session, Message } from '../types'
import { SessionList } from '../components/SessionList'
import { ChatMessage } from '../components/ChatMessage'
import { ChatInput } from '../components/ChatInput'

export function ChatPage() {
  const [sessions, setSessions] = useState<Session[]>([])
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const { isAuthenticated, logout } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login')
      return
    }
    loadSessions()
  }, [isAuthenticated, navigate])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const loadSessions = async () => {
    try {
      const response = await chat.getSessions()
      setSessions(response.data)
    } catch {
      console.error('Failed to load sessions')
    }
  }

  const loadMessages = async (sessionId: string) => {
    try {
      const response = await chat.getMessages(sessionId)
      setMessages(response.data)
      setActiveSessionId(sessionId)
    } catch {
      console.error('Failed to load messages')
    }
  }

  const handleSend = async (content: string) => {
    if (!content.trim()) return

    const userMessage: Message = { role: 'user', content }
    setMessages((prev) => [...prev, userMessage])
    setIsLoading(true)

    try {
      const response = await chat.sendMessage([
        { role: 'user', content, session_id: activeSessionId || undefined },
      ])

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.data.content,
      }
      setMessages((prev) => [...prev, assistantMessage])

      if (!activeSessionId && response.data.session_id) {
        setActiveSessionId(response.data.session_id)
        loadSessions()
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Xin lỗi, có lỗi xảy ra. Vui lòng thử lại.' },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  const handleDeleteSession = async (sessionId: string) => {
    try {
      await chat.deleteSession(sessionId)
      setSessions((prev) => prev.filter((s) => s.id !== sessionId))
      if (activeSessionId === sessionId) {
        setActiveSessionId(null)
        setMessages([])
      }
    } catch {
      console.error('Failed to delete session')
    }
  }

  const handleNewChat = () => {
    setActiveSessionId(null)
    setMessages([])
  }

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  return (
    <div className="chat-page">
      <div className="sidebar">
        <div className="sidebar-header">
          <h2>VIE Law</h2>
          <button onClick={handleLogout}>Đăng xuất</button>
        </div>
        <SessionList
          sessions={sessions}
          activeSessionId={activeSessionId}
          onSelectSession={loadMessages}
          onDeleteSession={handleDeleteSession}
          onNewChat={handleNewChat}
        />
      </div>
      <div className="chat-main">
        <div className="messages">
          {messages.length === 0 ? (
            <div className="empty-state">
              <h3>Xin chào!</h3>
              <p>Hỏi tôi bất cứ điều gì về luật pháp Việt Nam.</p>
            </div>
          ) : (
            messages.map((msg, index) => (
              <ChatMessage key={index} message={msg} />
            ))
          )}
          <div ref={messagesEndRef} />
        </div>
        <ChatInput onSend={handleSend} isLoading={isLoading} />
      </div>
    </div>
  )
}
