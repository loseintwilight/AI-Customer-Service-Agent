<script setup lang="ts">
import { onMounted } from 'vue'
import { useChatStore } from '@/stores/chat'
import Sidebar from '@/components/Sidebar.vue'
import ChatHeader from '@/components/ChatHeader.vue'
import ChatMessages from '@/components/ChatMessages.vue'
import ChatInput from '@/components/ChatInput.vue'

const store = useChatStore()

onMounted(() => {
  store.init()
})
</script>

<template>
  <div class="app-layout">
    <Sidebar />
    <div class="main-area">
      <div class="bg-layer"></div>
      <div class="main-content">
        <ChatHeader />
        <ChatMessages />
        <ChatInput />
      </div>
    </div>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  background: #ffffff;
}

.main-area {
  flex: 1;
  position: relative;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.bg-layer {
  position: absolute;
  inset: 0;
  background-image: url('/bg.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  z-index: 0;
}

.bg-layer::after {
  content: '';
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.65);
}

.main-content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
}
</style>