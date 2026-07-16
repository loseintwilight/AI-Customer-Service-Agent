<script setup lang="ts">
import { ref } from 'vue'
import { useChatStore } from '@/stores/chat'

const store = useChatStore()
const inputText = ref('')
const inputRef = ref<HTMLTextAreaElement>()

function autoResize() {
  const el = inputRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 120) + 'px'
}

function handleSend() {
  const text = inputText.value.trim()
  if (!text || store.isLoading || store.isStreaming) return
  inputText.value = ''
  if (inputRef.value) {
    inputRef.value.style.height = 'auto'
  }
  store.sendMessage(text)
}

function handleStop() {
  store.cancelStream()
}

function handleKeydown(e: KeyboardEvent) {
  if (store.isStreaming || store.isLoading) return
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}
</script>

<template>
  <div class="input-area">
    <div class="input-container">
      <!-- 左侧工具栏 -->
      <div class="input-toolbar">
        <button class="tool-btn" :disabled="store.isStreaming" title="上传文件或图片">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="16"/>
            <line x1="8" y1="12" x2="16" y2="12"/>
          </svg>
        </button>
        <button class="tool-btn" :disabled="store.isStreaming" title="更多功能">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="5" r="1.5"/>
            <circle cx="12" cy="12" r="1.5"/>
            <circle cx="12" cy="19" r="1.5"/>
          </svg>
        </button>
      </div>

      <!-- 输入框 -->
      <textarea
        ref="inputRef"
        v-model="inputText"
        class="chat-input"
        :class="{ 'streaming': store.isStreaming }"
        :placeholder="store.isStreaming ? '正在回复中...' : '输入消息，Enter 发送，Shift+Enter 换行'"
        :readonly="store.isStreaming"
        rows="1"
        @input="autoResize"
        @keydown="handleKeydown"
      ></textarea>

      <!-- 发送/停止按钮 - 内嵌在输入框右下角 -->
      <button
        v-if="!store.isStreaming && !store.isLoading"
        class="action-btn send-btn"
        :class="{ active: inputText.trim() }"
        :disabled="!inputText.trim()"
        @click="handleSend"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" stroke="none">
          <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
        </svg>
      </button>

      <!-- 流式时的停止按钮 -->
      <button
        v-else-if="store.isStreaming"
        class="action-btn stop-btn"
        @click="handleStop"
        title="停止生成"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" stroke="none">
          <rect x="4" y="4" width="16" height="16" rx="2"/>
        </svg>
      </button>
    </div>
    <p class="input-hint">AI 回复仅供参考，请以实际情况为准</p>
  </div>
</template>

<style scoped>
.input-area {
  padding: 8px 24px 16px;
  background: #ffffff;
}

.input-container {
  display: flex;
  align-items: flex-end;
  gap: 2px;
  background: #ffffff;
  border: 1px solid #d1d1d6;
  border-radius: 20px;
  padding: 6px 6px 6px 12px;
  max-width: 860px;
  margin: 0 auto;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.input-container:focus-within {
  border-color: #0066cc;
  box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.08);
}

.input-toolbar {
  display: flex;
  align-items: center;
  gap: 0px;
  flex-shrink: 0;
  padding-bottom: 2px;
}

.tool-btn {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  border: none;
  background: transparent;
  color: #86868b;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}

.tool-btn:hover:not(:disabled) {
  background: #f5f5f7;
  color: #1d1d1f;
}

.tool-btn:disabled {
  cursor: not-allowed;
  opacity: 0.4;
}

.chat-input {
  flex: 1;
  border: none;
  outline: none;
  resize: none;
  font-size: 14px;
  line-height: 1.6;
  font-family: inherit;
  max-height: 120px;
  min-height: 26px;
  color: #1d1d1f;
  background: transparent;
  padding: 4px 4px 4px 0;
}

.chat-input::placeholder {
  color: #c7c7c7;
  font-size: 14px;
}

.chat-input.streaming {
  cursor: not-allowed;
  opacity: 0.6;
}

.action-btn {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.send-btn {
  background: #f0f0f0;
  color: #c7c7c7;
  cursor: pointer;
}

.send-btn.active {
  background: #0066cc;
  color: white;
  cursor: pointer;
}

.send-btn.active:hover {
  background: #0055b3;
}

.send-btn:disabled {
  cursor: not-allowed;
}

.stop-btn {
  background: #ffffff;
  color: #1d1d1f;
  border: 1px solid #d1d1d6;
  cursor: pointer;
}

.stop-btn:hover {
  background: #f5f5f7;
  border-color: #86868b;
}

.input-hint {
  text-align: center;
  font-size: 11px;
  color: #c7c7c7;
  margin-top: 6px;
  letter-spacing: 0.2px;
}
</style>