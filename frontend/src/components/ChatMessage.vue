<script setup lang="ts">
import { computed } from 'vue'
import { marked } from 'marked'
import ChartView from './ChartView.vue'
import { useChatStore } from '@/stores/chat'
import type { Message } from '@/stores/chat'

const props = defineProps<{
  message: Message
}>()

const store = useChatStore()

const renderedContent = computed(() => {
  if (!props.message.content) return ''
  return marked.parse(props.message.content, { breaks: true }) as string
})

function formatTime(ts: number) {
  const d = new Date(ts)
  const now = new Date()
  const isToday = d.toDateString() === now.toDateString()
  if (isToday) {
    return d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }
  return d.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}
</script>

<template>
  <div class="message-wrapper" :class="message.type">
    <!-- AI 头像：左侧 -->
    <div v-if="message.type === 'ai'" class="avatar av-ai">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 2a8 8 0 0 0-8 8c0 2.5 1.2 4.7 3 6l-1 4 4-2.5c.6.3 1.3.5 2 .5a8 8 0 1 0 0-16Z"/>
        <path d="M9 10h.01"/>
        <path d="M15 10h.01"/>
        <path d="M12 14c.5.5 1.3 1 2 1s1.5-.5 2-1"/>
      </svg>
    </div>

    <!-- 消息内容区域 -->
    <div class="body" :class="message.type">
      <!-- AI 消息：显示气泡内容 -->
      <div v-if="message.type === 'ai'" class="bubble bubble-ai">
        <!-- 正在流式且无内容 → 显示加载点 -->
        <div v-if="!message.content && message.isStreaming" class="loading-dots">
          <span class="dot"></span>
          <span class="dot"></span>
          <span class="dot"></span>
        </div>
        <!-- 有内容 → 渲染 Markdown -->
        <div v-else-if="message.content" class="message-content" :class="{ 'typing-cursor': message.isStreaming }" v-html="renderedContent"></div>
        <!-- 图表 -->
        <ChartView v-if="message.chartData" :data="message.chartData" />
        <!-- 图片 -->
        <img v-if="message.imageUrl" :src="message.imageUrl" class="msg-image" alt="AI 生成图片" />
        <!-- 流式时的停止按钮 -->
        <button
          v-if="message.isStreaming"
          class="stop-stream-btn"
          @click="store.cancelStream()"
          title="停止生成"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" stroke="none">
            <rect x="4" y="4" width="16" height="16" rx="2"/>
          </svg>
          <span>停止生成</span>
        </button>
        <div class="msg-time">{{ formatTime(message.timestamp) }}</div>
      </div>

      <!-- 用户消息：显示气泡内容 -->
      <div v-else class="bubble bubble-user">
        <div class="message-content" v-html="renderedContent"></div>
        <div class="msg-time">{{ formatTime(message.timestamp) }}</div>
      </div>
    </div>

    <!-- 用户头像：右侧 -->
    <div v-if="message.type === 'user'" class="avatar av-user">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
        <circle cx="12" cy="7" r="4"/>
      </svg>
    </div>
  </div>
</template>

<style scoped>
.message-wrapper {
  display: flex;
  gap: 10px;
  padding: 12px 24px;
  max-width: 860px;
  margin: 0 auto;
  width: 100%;
  animation: slideIn 0.25s ease-out;
}

.message-wrapper.user {
  justify-content: flex-end;
}

.avatar {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 4px;
}

.av-ai {
  background: #f0f0f0;
  color: #86868b;
}

.av-user {
  background: #f0f0f0;
  color: #86868b;
}

.body {
  max-width: 75%;
  min-width: 0;
}

.body.user {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.body.ai {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.bubble {
  padding: 10px 16px;
  font-size: 14px;
  line-height: 1.7;
  word-break: break-word;
  white-space: pre-wrap;
}

/* 用户气泡：浅灰底色，圆角居右 */
.bubble-user {
  background: #f0f0f0;
  color: #1d1d1f;
  border-radius: 16px 16px 4px 16px;
}

/* AI 气泡：纯白，无边框，居左 */
.bubble-ai {
  background: transparent;
  color: #1d1d1f;
  padding: 10px 0;
}

.msg-time {
  font-size: 11px;
  color: #c7c7c7;
  margin-top: 4px;
}

.bubble-user .msg-time {
  text-align: right;
}

.msg-image {
  max-width: 100%;
  max-height: 400px;
  border-radius: 8px;
  margin-top: 8px;
}

/* 停止生成按钮 */
.stop-stream-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-top: 8px;
  padding: 4px 12px;
  border: 1px solid #d1d1d6;
  border-radius: 6px;
  background: #ffffff;
  color: #86868b;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.15s;
}

.stop-stream-btn:hover {
  background: #f5f5f7;
  color: #1d1d1f;
  border-color: #86868b;
}

/* 加载点动画 */
.loading-dots {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 0;
}

.loading-dots .dot {
  width: 7px;
  height: 7px;
  background: #86868b;
  border-radius: 50%;
  animation: dotBounce 1.4s infinite ease-in-out both;
}

.loading-dots .dot:nth-child(1) { animation-delay: -0.32s; }
.loading-dots .dot:nth-child(2) { animation-delay: -0.16s; }
.loading-dots .dot:nth-child(3) { animation-delay: 0s; }

@keyframes dotBounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>