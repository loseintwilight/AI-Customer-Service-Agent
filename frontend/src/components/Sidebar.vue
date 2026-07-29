<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useChatStore } from '@/stores/chat'

const store = useChatStore()
const searchQuery = ref('')
const hoverId = ref<string>('')
const menuOpenId = ref<string>('')

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

function toggleMenu(id: string, e: Event) {
  e.stopPropagation()
  menuOpenId.value = menuOpenId.value === id ? '' : id
}

function closeMenu() {
  menuOpenId.value = ''
}

function handleRename(session: any) {
  closeMenu()
  const newTitle = prompt('重命名对话', session.title)
  if (newTitle && newTitle.trim()) {
    session.title = newTitle.trim().slice(0, 30)
  }
}

function handleDelete(id: string) {
  closeMenu()
  if (confirm('确定删除此对话？')) {
    store.deleteSession(id)
  }
}

onMounted(() => {
  document.addEventListener('click', closeMenu)
})

onUnmounted(() => {
  document.removeEventListener('click', closeMenu)
})
</script>

<template>
  <div class="sidebar">
    <!-- 顶部搜索框 -->
    <div class="sidebar-search">
      <div class="search-box">
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
      <span class="plus-icon">+</span>
      <span>新对话</span>
    </button>

    <!-- 会话列表 -->
    <div class="session-list">
      <div
        v-for="session in filteredSessions"
        :key="session.id"
        class="session-item"
        :class="{ active: session.id === store.currentSessionId }"
        @click="store.switchSession(session.id); closeMenu()"
        @mouseenter="hoverId = session.id"
        @mouseleave="hoverId = ''"
      >
        <div class="session-content">
          <div class="session-title">{{ session.title }}</div>
          <div class="session-time">{{ formatTime(session.createdAt) }}</div>
        </div>
        <!-- 三点菜单按钮 -->
        <button
          v-show="hoverId === session.id || menuOpenId === session.id"
          class="more-btn"
          @click="toggleMenu(session.id, $event)"
          title="更多操作"
        >
          ⋯
        </button>
        <!-- 下拉菜单 -->
        <div v-if="menuOpenId === session.id" class="dropdown-menu" @click.stop>
          <div class="menu-item" @click="handleRename(session)">
            <span class="menu-icon">✎</span>
            <span>重命名</span>
          </div>
          <div class="menu-item menu-item-danger" @click="handleDelete(session.id)">
            <span class="menu-icon">×</span>
            <span>删除</span>
          </div>
        </div>
      </div>

      <div v-if="filteredSessions.length === 0" class="empty-hint">
        <p>{{ searchQuery ? '未找到相关对话' : '暂无对话记录，开始一个新对话吧' }}</p>
      </div>
    </div>

    <!-- 底部用户信息 -->
    <div class="sidebar-footer">
      <div class="user-info">
        <div class="user-avatar">
          <img src="/avatar.png" alt="用户" />
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
  position: relative;
  z-index: 10;
}

.sidebar-search {
  padding: 16px 16px 8px;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
}

.search-input {
  width: 100%;
  height: 36px;
  padding: 0 12px;
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
  gap: 8px;
  margin: 8px 16px;
  height: 36px;
  border: 1px solid #e5e5e5;
  border-radius: 8px;
  background: #ffffff;
  color: #1d1d1f;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  padding: 0 14px;
  transition: all 0.2s;
}

.plus-icon {
  font-size: 16px;
  color: #86868b;
  font-weight: 400;
  line-height: 1;
}

.new-chat-btn:hover {
  background: #f5f5f7;
  border-color: #d1d1d6;
}

.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 4px 8px;
  position: relative;
}

.session-item {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 10px 12px;
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
  background: #e8e8ed;
}

.session-item.active .session-title {
  font-weight: 600;
  color: #0066cc;
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

.more-btn {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  border-radius: 4px;
  border: none;
  background: transparent;
  color: #86868b;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: bold;
  line-height: 1;
  transition: all 0.15s;
}

.more-btn:hover {
  background: #d1d1d6;
  color: #1d1d1f;
}

/* 下拉菜单 */
.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 8px;
  margin-top: 4px;
  background: #ffffff;
  border: 1px solid #e5e5e5;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  min-width: 120px;
  z-index: 100;
  overflow: hidden;
  padding: 4px 0;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  font-size: 13px;
  color: #1d1d1f;
  cursor: pointer;
  transition: background 0.15s;
}

.menu-item:hover {
  background: #f5f5f7;
}

.menu-item-danger {
  color: #ff3b30;
}

.menu-item-danger:hover {
  background: #fff0ef;
}

.menu-icon {
  width: 14px;
  text-align: center;
  font-size: 14px;
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
  font-size: 12px;
  font-weight: 600;
  overflow: hidden;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-name {
  font-size: 13px;
  font-weight: 500;
  color: #1d1d1f;
}
</style>