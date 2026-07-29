<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import { useChatStore } from '@/stores/chat'
import ChatMessage from './ChatMessage.vue'

const store = useChatStore()
const messagesRef = ref<HTMLDivElement>()

const suggestions = [
  { text: '查询薪资前5的教师', icon: '★' },
  { text: '统计学生的绩点分布', icon: '◆' },
  { text: '查询各个课程的预约占比', icon: '●' },
  { text: '查询男学生女学生各所占比例', icon: '▲' },
  { text: '根据入职年份查询教师薪资走向', icon: '▼' },
  { text: '查询预约课程的取消比率', icon: '■' },
]

watch(
  () => store.messages.length,
  async () => {
    await nextTick()
    scrollToBottom()
  },
  { deep: true }
)

watch(
  () => {
    const msgs = store.messages
    return msgs[msgs.length - 1]?.content
  },
  async () => {
    await nextTick()
    scrollToBottom()
  }
)

function scrollToBottom() {
  if (messagesRef.value) {
    messagesRef.value.scrollTop = messagesRef.value.scrollHeight
  }
}
</script>

<template>
  <div ref="messagesRef" class="messages-area">
    <!-- 空白欢迎页 -->
    <div v-if="store.messages.length === 0" class="welcome">
      <div class="welcome-card">
        <h2 class="welcome-title">有什么我能帮你的吗？</h2>
        <p class="welcome-desc">我可以帮你查询数据、分析报表、生成图表，试试下面的快捷提问</p>
        <div class="suggestion-grid">
          <div
            v-for="(s, i) in suggestions"
            :key="i"
            class="suggestion-card"
            @click="store.sendMessage(s.text)"
          >
            <span class="suggestion-icon">{{ s.icon }}</span>
            <span class="suggestion-text">{{ s.text }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 消息列表 -->
    <div v-for="msg in store.messages" :key="msg.id" class="msg-row">
      <ChatMessage :message="msg" />
    </div>
  </div>
</template>

<style scoped>
.messages-area {
  flex: 1;
  overflow-y: auto;
  background: transparent;
  position: relative;
}

.welcome {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 40px 24px;
}

.welcome-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  max-width: 520px;
  width: 100%;
  padding: 32px 24px;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.4);
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
}

.welcome-title {
  font-size: 26px;
  font-weight: 600;
  color: #1d1d1f;
  margin-bottom: 10px;
  letter-spacing: -0.3px;
}

.welcome-desc {
  font-size: 14px;
  color: #86868b;
  margin-bottom: 28px;
  line-height: 1.5;
}

.suggestion-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  width: 100%;
}

.suggestion-card {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(229, 229, 229, 0.8);
  border-radius: 10px;
  font-size: 13px;
  color: #1d1d1f;
  cursor: pointer;
  transition: all 0.15s;
  text-align: left;
}

.suggestion-card:hover {
  background: #ffffff;
  border-color: #0066cc;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 102, 204, 0.12);
}

.suggestion-icon {
  font-size: 14px;
  flex-shrink: 0;
  color: #667eea;
  font-weight: bold;
}

.suggestion-text {
  line-height: 1.4;
}

.msg-row {
  width: 100%;
}
</style>