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
        <button class="tool-btn" :disabled="store.isStreaming" title="上传文件或图片">+</button>
        <button class="tool-btn" :disabled="store.isStreaming" title="更多功能">···</button>
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

      <!-- 发送按钮 -->
      <button
        v-if="!store.isStreaming && !store.isLoading"
        class="action-btn send-btn"
        :class="{ active: inputText.trim() }"
        :disabled="!inputText.trim()"
        @click="handleSend"
      >
        发送
      </button>

      <!-- 停止按钮 -->
      <button
        v-else-if="store.isStreaming"
        class="action-btn stop-btn"
        @click="handleStop"
        title="停止生成"
      >
        停止
      </button>
    </div>
    <p class="input-hint">AI 回复仅供参考，请以实际情况为准</p>
  </div>
</template>

<style scoped>
.input-area {
  padding: 8px 24px 18px;
  background: transparent;
}

.input-container {
  display: flex;
  align-items: flex-end;
  gap: 2px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(209, 209, 214, 0.6);
  border-radius: 20px;
  padding: 6px 6px 6px 12px;
  max-width: 860px;
  margin: 0 auto;
  transition: border-color 0.2s, box-shadow 0.2s;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.input-container:focus-within {
  border-color: #0066cc;
  box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.08), 0 2px 12px rgba(0, 0, 0, 0.04);
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
  font-size: 16px;
  line-height: 1;
  transition: all 0.15s;
}

.tool-btn:hover:not(:disabled) {
  background: rgba(0, 0, 0, 0.05);
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
  height: 34px;
  border-radius: 17px;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  font-size: 13px;
  padding: 0 16px;
  font-weight: 500;
  letter-spacing: 0.5px;
}

.send-btn {
  background: #f0f0f0;
  color: #c7c7c7;
  cursor: pointer;
}

.send-btn.active {
  background: #1d1d1f;
  color: white;
  cursor: pointer;
}

.send-btn.active:hover {
  background: #000000;
}

.send-btn:disabled {
  cursor: not-allowed;
}

.stop-btn {
  background: #ffffff;
  color: #ff3b30;
  border: 1px solid #ff3b30;
  cursor: pointer;
}

.stop-btn:hover {
  background: #ff3b30;
  color: #ffffff;
}

.input-hint {
  text-align: center;
  font-size: 11px;
  color: #86868b;
  margin-top: 8px;
  letter-spacing: 0.2px;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.8);
}
</style>