<script setup lang="ts">
import { ref, computed } from 'vue'
import { useChatStore } from '@/stores/chat'

const store = useChatStore()
const searchQuery = ref('')

const filteredSessions = computed(() => {
  if (!searchQuery.value.trim()) return store.sessions
  return store.sessions.filter(s =>
    s.title.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

function formatTime(ts: number) {
  const d = new Date(ts)
  const now = new Date()
  const isToday = d.toDateString() === now.toDateString()
  if (isToday) {
    return d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }
  const yesterday = new Date(now)
  yesterday.setDate(yesterday.getDate() - 1)
  if (d.toDateString() === yesterday.toDateString()) {
    return '昨天'
  }
  return d.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
}
</script>

<template>
  <div class="sidebar">
    <!-- 顶部搜索框 -->
    <div class="sidebar-search">
      <div class="search-box">
        <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="11" cy="11" r="8"/>
          <line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
        <input
          v-model="searchQuery"
          type="text"
          class="search-input"
          placeholder="搜索对话"
        />
      </div>
    </div>

    <!-- 新对话按钮 -->
    <button class="new-chat-btn" @click="store.createNewSession()">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="12" y1="5" x2="12" y2="19"/>
        <line x1="5" y1="12" x2="19" y2="12"/>
      </svg>
      <span>新对话</span>
    </button>

    <!-- 会话列表 -->
    <div class="session-list">
      <div
        v-for="session in filteredSessions"
        :key="session.id"
        class="session-item"
        :class="{ active: session.id === store.currentSessionId }"
        @click="store.switchSession(session.id)"
      >
        <div class="session-content">
          <div class="session-title">{{ session.title }}</div>
          <div class="session-time">{{ formatTime(session.createdAt) }}</div>
        </div>
        <button
          class="delete-btn"
          @click.stop="store.deleteSession(session.id)"
          title="删除对话"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="3 6 5 6 21 6"/>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
          </svg>
        </button>
      </div>

      <div v-if="filteredSessions.length === 0" class="empty-hint">
        <p>{{ searchQuery ? '未找到相关对话' : '暂无对话记录，开始一个新对话吧' }}</p>
      </div>
    </div>

    <!-- 底部用户信息 -->
    <div class="sidebar-footer">
      <div class="user-info">
        <div class="user-avatar">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
        </div>
        <span class="user-name">用户</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.sidebar {
  width: 280px;
  min-width: 280px;
  height: 100%;
  background: #ffffff;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #e5e5e5;
}

.sidebar-search {
  padding: 16px 16px 8px;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 12px;
  color: #86868b;
  pointer-events: none;
}

.search-input {
  width: 100%;
  height: 36px;
  padding: 0 12px 0 36px;
  border: 1px solid #e5e5e5;
  border-radius: 8px;
  font-size: 13px;
  color: #1d1d1f;
  background: #f5f5f7;
  outline: none;
  transition: all 0.2s;
}

.search-input::placeholder {
  color: #86868b;
}

.search-input:focus {
  border-color: #0066cc;
  background: #ffffff;
  box-shadow: 0 0 0 2px rgba(0, 102, 204, 0.08);
}

.new-chat-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin: 8px 16px;
  height: 36px;
  border: 1px solid #e5e5e5;
  border-radius: 8px;
  background: #ffffff;
  color: #1d1d1f;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.new-chat-btn:hover {
  background: #f5f5f7;
  border-color: #d1d1d6;
}

.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 4px 8px;
}

.session-item {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s;
  margin-bottom: 2px;
  position: relative;
}

.session-item:hover {
  background: #f5f5f7;
}

.session-item.active {
  background: #f0f0f0;
}

.session-item.active .session-title {
  font-weight: 500;
}

.session-content {
  flex: 1;
  min-width: 0;
}

.session-title {
  font-size: 13px;
  color: #1d1d1f;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.4;
}

.session-time {
  font-size: 11px;
  color: #86868b;
  margin-top: 2px;
}

.delete-btn {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  border-radius: 6px;
  border: none;
  background: transparent;
  color: #86868b;
  cursor: pointer;
  display: none;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}

.session-item:hover .delete-btn {
  display: flex;
}

.delete-btn:hover {
  background: #f0f0f0;
  color: #ff3b30;
}

.empty-hint {
  text-align: center;
  padding: 32px 16px;
  color: #86868b;
  font-size: 13px;
  line-height: 1.6;
}

.sidebar-footer {
  padding: 12px 16px;
  border-top: 1px solid #e5e5e5;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s;
}

.user-info:hover {
  background: #f5f5f7;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #86868b;
}

.user-name {
  font-size: 13px;
  font-weight: 500;
  color: #1d1d1f;
}
</style>