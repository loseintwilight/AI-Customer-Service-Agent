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
      <img src="/avatar.png" alt="AI" />
    </div>

    <!-- 消息内容区域 -->
    <div class="body" :class="message.type">
      <!-- AI 消息 -->
      <div v-if="message.type === 'ai'" class="bubble bubble-ai">
        <div v-if="!message.content && message.isStreaming" class="loading-dots">
          <span class="dot"></span>
          <span class="dot"></span>
          <span class="dot"></span>
        </div>
        <div v-else-if="message.content" class="message-content" :class="{ 'typing-cursor': message.isStreaming }" v-html="renderedContent"></div>
        <ChartView v-if="message.chartData" :data="message.chartData" />
        <img v-if="message.imageUrl" :src="message.imageUrl" class="msg-image" alt="AI 生成图片" />
        <button
          v-if="message.isStreaming"
          class="stop-stream-btn"
          @click="store.cancelStream()"
          title="停止生成"
        >
          停止生成
        </button>
        <!-- 已停止提示（参考豆包） -->
        <div v-else-if="message.isStopped" class="stopped-hint">
          <span class="stopped-icon">⏹</span>
          <span>已停止</span>
        </div>
      </div>

      <!-- 用户消息 -->
      <div v-else class="bubble bubble-user">
        <div class="message-content" v-html="renderedContent"></div>
      </div>

      <!-- 时间戳（独立显示在气泡下方） -->
      <div class="msg-time">{{ formatTime(message.timestamp) }}</div>
    </div>

    <!-- 用户头像：右侧 -->
    <div v-if="message.type === 'user'" class="avatar av-user">
      <img src="/avatar.png" alt="用户" />
    </div>
  </div>
</template>

<style scoped>
.message-wrapper {
  display: flex;
  gap: 12px;
  padding: 16px 24px;
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
  animation: slideIn 0.25s ease-out;
}

.message-wrapper.user {
  justify-content: flex-end;
}

.avatar {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 2px;
  font-size: 13px;
  font-weight: 600;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.av-ai {
  background: #ffffff;
  border: 1px solid #e5e5e5;
}

.av-user {
  background: #ffffff;
  border: 1px solid #e5e5e5;
}

.body {
  max-width: 75%;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.body.user {
  align-items: flex-end;
}

.body.ai {
  align-items: flex-start;
}

.bubble {
  padding: 12px 16px;
  font-size: 14px;
  line-height: 1.65;
  word-break: break-word;
  position: relative;
  display: inline-block;
  width: fit-content;
  max-width: 100%;
}

/* 用户气泡：纯浅灰底色 */
.bubble-user {
  background: #f0f0f0;
  color: #1d1d1f;
  border-radius: 16px;
  border: none;
}

/* AI 气泡：浅灰底色包裹，参考豆包样式 */
.bubble-ai {
  background: #f0f0f0;
  color: #1d1d1f;
  border-radius: 16px;
  border: none;
}

.msg-time {
  font-size: 11px;
  color: #c7c7c7;
  margin-top: 4px;
  padding: 0 2px;
  line-height: 1;
  width: 100%;
}

.body.user .msg-time {
  text-align: right;
}

.body.ai .msg-time {
  text-align: left;
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

/* 已停止提示（参考豆包） */
.stopped-hint {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  margin-top: 8px;
  padding: 3px 10px;
  border-radius: 6px;
  background: rgba(0, 0, 0, 0.04);
  color: #86868b;
  font-size: 12px;
  line-height: 1.4;
}

.stopped-icon {
  font-size: 10px;
  color: #86868b;
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