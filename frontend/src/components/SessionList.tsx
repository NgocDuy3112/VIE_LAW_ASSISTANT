import { Session } from '../types'

interface SessionListProps {
  sessions: Session[]
  activeSessionId: string | null
  onSelectSession: (sessionId: string) => void
  onDeleteSession: (sessionId: string) => void
  onNewChat: () => void
}

export function SessionList({
  sessions,
  activeSessionId,
  onSelectSession,
  onDeleteSession,
  onNewChat,
}: SessionListProps) {
  return (
    <div className="session-list">
      <button className="new-chat-btn" onClick={onNewChat}>
        + Chat mới
      </button>
      <div className="sessions">
        {sessions.map((session) => (
          <div
            key={session.id}
            className={`session-item ${session.id === activeSessionId ? 'active' : ''}`}
            onClick={() => onSelectSession(session.id)}
          >
            <span className="session-title">
              {session.title || 'Cuộc trò chuyện mới'}
            </span>
            <button
              className="delete-btn"
              onClick={(e) => {
                e.stopPropagation()
                onDeleteSession(session.id)
              }}
            >
              ×
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
