<script setup lang="ts">
import { ref } from 'vue'
import { useChatStore } from '@/stores/chat'

const store = useChatStore()
const showModelMenu = ref(false)
const currentModel = ref('qwen-plus')

const models = [
  { value: 'qwen-plus', label: 'qwen-plus' },
  { value: 'qwen-max', label: 'qwen-max' },
  { value: 'deepseek', label: 'DeepSeek' },
]

function selectModel(model: string) {
  currentModel.value = model
  showModelMenu.value = false
}
</script>

<template>
  <div class="chat-header">
    <div class="header-center">
      <h1 class="header-title">{{ store.currentSession?.title || '新对话' }}</h1>
    </div>
    <div class="header-right">
      <div class="model-selector" @click="showModelMenu = !showModelMenu">
        <span class="model-label">{{ currentModel }}</span>
        <svg
          class="model-arrow"
          :class="{ rotated: showModelMenu }"
          width="14" height="14" viewBox="0 0 24 24"
          fill="none" stroke="currentColor" stroke-width="2"
          stroke-linecap="round" stroke-linejoin="round"
        >
          <polyline points="6 9 12 15 18 9"/>
        </svg>
        <div v-if="showModelMenu" class="model-dropdown" @click.stop>
          <div
            v-for="m in models"
            :key="m.value"
            class="model-option"
            :class="{ selected: m.value === currentModel }"
            @click="selectModel(m.value)"
          >
            {{ m.label }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-header {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px 24px;
  background: #ffffff;
  border-bottom: 1px solid #e5e5e5;
  min-height: 52px;
}

.header-center {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  text-align: center;
}

.header-title {
  font-size: 15px;
  font-weight: 600;
  color: #1d1d1f;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 300px;
}

.header-right {
  margin-left: auto;
}

.model-selector {
  position: relative;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border: 1px solid #e5e5e5;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s;
  user-select: none;
}

.model-selector:hover {
  background: #f5f5f7;
}

.model-label {
  font-size: 12px;
  color: #86868b;
  font-weight: 500;
}

.model-arrow {
  color: #86868b;
  transition: transform 0.2s;
}

.model-arrow.rotated {
  transform: rotate(180deg);
}

.model-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 4px;
  background: #ffffff;
  border: 1px solid #e5e5e5;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
  min-width: 140px;
  z-index: 100;
  overflow: hidden;
}

.model-option {
  padding: 8px 14px;
  font-size: 13px;
  color: #1d1d1f;
  cursor: pointer;
  transition: background 0.15s;
}

.model-option:hover {
  background: #f5f5f7;
}

.model-option.selected {
  color: #0066cc;
  font-weight: 500;
}
</style>