import { ref, readonly } from 'vue'
import {
  createSession,
  listSessions,
  getSessionMessages,
  sendMessage,
  deleteSession,
  type Session,
  type SessionMessage,
} from '@/api/client'
import { useWebSocket } from './useWebSocket'

export function useSession() {
  const sessions = ref<Session[]>([])
  const currentSession = ref<Session | null>(null)
  const messages = ref<SessionMessage[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const { events, connected } = useWebSocket(
    () => currentSession.value?.id || ''
  )

  async function loadSessions(workspace: string) {
    try {
      sessions.value = await listSessions(workspace)
    } catch (e: any) {
      error.value = e.message
    }
  }

  async function selectSession(session: Session) {
    currentSession.value = session
    loading.value = true
    try {
      messages.value = await getSessionMessages(session.id)
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function createNewSession(workspace: string) {
    loading.value = true
    try {
      const result = await createSession(workspace)
      const session: Session = {
        id: result.session_id,
        workspace: result.workspace,
        created_at: result.created_at,
        message_count: 0,
      }
      sessions.value.unshift(session)
      currentSession.value = session
      messages.value = []
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function send(content: string) {
    if (!currentSession.value) return
    loading.value = true
    error.value = null
    try {
      messages.value.push({ role: 'user', content })
      await sendMessage(currentSession.value.id, content)
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function removeSession(sessionId: string) {
    try {
      await deleteSession(sessionId)
      sessions.value = sessions.value.filter(s => s.id !== sessionId)
      if (currentSession.value?.id === sessionId) {
        currentSession.value = null
        messages.value = []
      }
    } catch (e: any) {
      error.value = e.message
    }
  }

  return {
    sessions: readonly(sessions),
    currentSession: readonly(currentSession),
    messages: readonly(messages),
    loading: readonly(loading),
    error: readonly(error),
    events,
    connected,
    loadSessions,
    selectSession,
    createNewSession,
    send,
    removeSession,
  }
}
