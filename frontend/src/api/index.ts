import axios from 'axios'

const API_BASE = ''

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
})

export interface ChartData {
  title: string
  xAxis: string[]
  series: number[]
  labels: string[]
  analysis: string
}

export interface ChatHistory {
  session_id: string
  messages: Array<{
    messageType: 'USER' | 'ASSISTANT'
    text: string
  }>
}

// 普通对话
export async function sendChat(msg: string, sessionId: string) {
  const res = await api.get('/ai/chat', {
    params: { msg, session_id: sessionId },
  })
  return res.data
}

// 流式对话 — 返回 EventSource
export function createStreamChat(msg: string, sessionId: string): EventSource {
  const url = `${API_BASE}/ai/stream?msg=${encodeURIComponent(msg)}&session_id=${encodeURIComponent(sessionId)}`
  return new EventSource(url)
}

// 获取对话历史
export async function getChatHistory(sessionId: string) {
  const res = await api.get('/ai/history', {
    params: { session_id: sessionId },
  })
  return res.data
}

// 删除对话历史
export async function deleteChatHistory(sessionId: string) {
  const res = await api.delete('/ai/history', {
    params: { session_id: sessionId },
  })
  return res.data
}

// BI 图表
export async function getCharts(text: string) {
  const res = await api.get('/ai/charts', {
    params: { text },
  })
  return res.data as ChartData
}

// AI 生图
export function getImageUrl(prompt: string): string {
  return `${API_BASE}/ai/image?prompt=${encodeURIComponent(prompt)}`
}

// Text2SQL
export async function text2sql(msg: string) {
  const res = await api.get('/ai/text2sql', {
    params: { msg },
  })
  return res.data
}