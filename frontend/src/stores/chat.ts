import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { deleteChatHistory, getCharts } from '@/api/index'
import type { ChartData } from '@/api/index'

export interface Message {
  id: string
  type: 'user' | 'ai'
  content: string
  timestamp: number
  isStreaming?: boolean
  chartData?: ChartData | null
  imageUrl?: string
}

export interface Session {
  id: string
  title: string
  createdAt: number
  messages: Message[]
}

export const useChatStore = defineStore('chat', () => {
  const sessions = ref<Session[]>([])
  const currentSessionId = ref<string>('')
  const isStreaming = ref(false)
  const isLoading = ref(false)

  const currentSession = computed(() => {
    return sessions.value.find(s => s.id === currentSessionId.value)
  })

  const messages = computed(() => {
    return currentSession.value?.messages || []
  })

  function generateId(): string {
    return Date.now().toString(36) + Math.random().toString(36).slice(2, 8)
  }

  function createNewSession() {
    const id = generateId()
    const session: Session = {
      id,
      title: '新对话',
      createdAt: Date.now(),
      messages: [],
    }
    sessions.value.unshift(session)
    currentSessionId.value = id
    return id
  }

  function switchSession(id: string) {
    currentSessionId.value = id
  }

  function deleteSession(id: string) {
    const idx = sessions.value.findIndex(s => s.id === id)
    if (idx === -1) return
    sessions.value.splice(idx, 1)
    if (currentSessionId.value === id) {
      if (sessions.value.length > 0) {
        currentSessionId.value = sessions.value[0].id
      } else {
        currentSessionId.value = ''
      }
    }
    deleteChatHistory(id).catch(() => {})
  }

  function addMessage(type: 'user' | 'ai', content: string, options?: {
    chartData?: ChartData | null
    imageUrl?: string
    isStreaming?: boolean
  }) {
    if (!currentSession.value) return
    const msg: Message = {
      id: generateId(),
      type,
      content,
      timestamp: Date.now(),
      isStreaming: options?.isStreaming || false,
      chartData: options?.chartData || null,
      imageUrl: options?.imageUrl,
    }
    currentSession.value.messages.push(msg)
    if (type === 'user' && currentSession.value.messages.filter(m => m.type === 'user').length === 1) {
      currentSession.value.title = content.slice(0, 30) + (content.length > 30 ? '...' : '')
    }
    return msg
  }

  function updateLastMessage(content: string, append = false) {
    if (!currentSession.value) return
    const last = currentSession.value.messages[currentSession.value.messages.length - 1]
    if (last && last.type === 'ai') {
      if (append) {
        last.content += content
      } else {
        last.content = content
      }
    }
  }

  function setLastMessageStreaming(streaming: boolean) {
    if (!currentSession.value) return
    const last = currentSession.value.messages[currentSession.value.messages.length - 1]
    if (last && last.type === 'ai') {
      last.isStreaming = streaming
    }
  }

  function setLastMessageChartData(chartData: ChartData | null) {
    if (!currentSession.value) return
    const last = currentSession.value.messages[currentSession.value.messages.length - 1]
    if (last && last.type === 'ai') {
      last.chartData = chartData
    }
  }

  /** 重置所有加载状态 */
  function resetLoadingState() {
    isStreaming.value = false
    isLoading.value = false
    setLastMessageStreaming(false)
    currentEventSource = null
  }

  /** 中断当前流式输出 */
  function cancelStream() {
    if (currentEventSource) {
      currentEventSource.close()
      currentEventSource = null
    }
    // 如果流式从未收到数据，删除空的 AI 占位消息
    if (currentSession.value) {
      const msgs = currentSession.value.messages
      const last = msgs[msgs.length - 1]
      if (last && last.type === 'ai' && !last.content && !last.chartData) {
        msgs.pop()
      }
    }
    resetLoadingState()
  }

  async function sendMessage(msg: string) {
    // 确保有当前会话
    if (!currentSession.value) createNewSession()
    if (!currentSession.value) return

    const sessionId = currentSessionId.value

    // 添加用户消息
    addMessage('user', msg)

    // 设置加载状态
    isStreaming.value = true
    isLoading.value = true

    // 添加空的 AI 占位消息，显示加载点
    addMessage('ai', '', { isStreaming: true })

    currentEventSource = null

    try {
      // 判断是否为图表类请求
      const chartKeywords = ['图表', '报表', '统计', '分布', '占比', '比例', '趋势', '薪资', '绩点', '课时', '预约', '前', '排名']
      const isChartRequest = chartKeywords.some(k => msg.includes(k))

      if (isChartRequest) {
        const chartData = await getCharts(msg)
        if (chartData && chartData.title && chartData.series && chartData.series.length > 0) {
          resetLoadingState()
          updateLastMessage(chartData.analysis || '')
          setLastMessageChartData(chartData)
          return
        }
        // 图表请求无有效数据，继续走 SSE 对话
      }

      // 检查是否已被中断（例如图表请求期间）
      if (!isStreaming.value) return

      // SSE 流式对话
      const es = new EventSource(`/ai/stream?msg=${encodeURIComponent(msg)}&session_id=${encodeURIComponent(sessionId)}`)
      currentEventSource = es

      es.onmessage = (event) => {
        // 收到第一个 token 时关闭 loading
        if (isLoading.value) {
          isLoading.value = false
        }
        if (event.data === '[DONE]') {
          es.close()
          resetLoadingState()
          return
        }
        updateLastMessage(event.data, true)
      }

      es.onerror = () => {
        es.close()
        // 如果从未收到数据，补一个错误提示
        const last = currentSession.value?.messages
        const aiMsg = last?.[last.length - 1]
        if (aiMsg && aiMsg.type === 'ai' && !aiMsg.content) {
          updateLastMessage('抱歉，连接出错了，请稍后重试。')
        }
        resetLoadingState()
      }
    } catch (e: any) {
      // 图表请求出错时，兜底走 SSE 对话
      if (!currentEventSource) {
        try {
          const es = new EventSource(`/ai/stream?msg=${encodeURIComponent(msg)}&session_id=${encodeURIComponent(sessionId)}`)
          currentEventSource = es
          es.onmessage = (event) => {
            if (isLoading.value) isLoading.value = false
            if (event.data === '[DONE]') {
              es.close()
              resetLoadingState()
              return
            }
            updateLastMessage(event.data, true)
          }
          es.onerror = () => {
            es.close()
            const last = currentSession.value?.messages
            const aiMsg = last?.[last.length - 1]
            if (aiMsg && aiMsg.type === 'ai' && !aiMsg.content) {
              updateLastMessage('抱歉，连接出错了，请稍后重试。')
            }
            resetLoadingState()
          }
        } catch {
          const last = currentSession.value?.messages
          const aiMsg = last?.[last.length - 1]
          if (aiMsg && aiMsg.type === 'ai' && !aiMsg.content) {
            updateLastMessage('抱歉，请求出错了，请稍后重试。')
          }
          resetLoadingState()
        }
      }
    }
  }

  function init() {
    if (sessions.value.length === 0) {
      createNewSession()
    }
  }

  return {
    sessions,
    currentSessionId,
    isStreaming,
    isLoading,
    currentSession,
    messages,
    createNewSession,
    switchSession,
    deleteSession,
    addMessage,
    updateLastMessage,
    setLastMessageStreaming,
    setLastMessageChartData,
    sendMessage,
    cancelStream,
    init,
  }
})