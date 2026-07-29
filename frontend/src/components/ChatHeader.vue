<script setup lang="ts">
import { ref } from 'vue'

const showModelMenu = ref(false)
const currentModel = ref('qwen-plus')

const models = [
  { value: 'qwen-plus', label: 'qwen-plus' },
  { value: 'qwen-max', label: 'qwen-max' },
  { value: 'qwen-turbo', label: 'qwen-turbo' },
  { value: 'deepseek', label: 'DeepSeek' },
]

function selectModel(model: string) {
  currentModel.value = model
  showModelMenu.value = false
}
</script>

<template>
  <div class="chat-header">
    <div class="header-left"></div>
    <div class="header-center">
      <h1 class="header-title">AI 智能客服</h1>
    </div>
    <div class="header-right">
      <div class="model-selector" @click="showModelMenu = !showModelMenu">
        <span class="model-label">{{ currentModel }}</span>
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
  justify-content: space-between;
  padding: 14px 24px;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(229, 229, 229, 0.6);
  min-height: 56px;
}

.header-left {
  width: 140px;
}

.header-center {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  text-align: center;
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  color: #1d1d1f;
  white-space: nowrap;
  letter-spacing: 0.2px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.model-selector {
  position: relative;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 5px 12px;
  border: 1px solid #e5e5e5;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.15s;
  user-select: none;
  background: #ffffff;
}

.model-selector:hover {
  background: #f5f5f7;
  border-color: #d1d1d6;
}

.model-label {
  font-size: 12px;
  color: #1d1d1f;
  font-weight: 500;
}

.model-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  right: 0;
  background: #ffffff;
  border: 1px solid #e5e5e5;
  border-radius: 10px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
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
  font-weight: 600;
  background: rgba(0, 102, 204, 0.05);
}
</style>