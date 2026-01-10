<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const messages = ref([])
const newMessage = ref('')
const loading = ref(true)
const chatContainer = ref(null)
let pollTimer = null

const fetchMessages = async (showLoading = false) => {
  if (showLoading) loading.value = true
  try {
    const res = await http.get('/alliance/chat/messages')
    if (res.data.ok) {
      const oldLength = messages.value.length
      messages.value = res.data.messages
      
      // 如果有新消息，滚动到底部
      if (messages.value.length > oldLength) {
        await nextTick()
        scrollToBottom()
      }
    }
  } catch (e) {
    console.error('获取联盟消息失败', e)
  } finally {
    if (showLoading) loading.value = false
  }
}

const sendMessage = async () => {
  if (!newMessage.value.trim()) return
  
  try {
    const res = await http.post('/alliance/chat/send', {
      content: newMessage.value
    })
    if (res.data.ok) {
      newMessage.value = ''
      await fetchMessages()
    } else {
      alert(res.data.error || '发送失败')
    }
  } catch (e) {
    alert(e.response?.data?.error || '发送失败')
  }
}

const scrollToBottom = () => {
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  fetchMessages(true)
  // 3秒轮询
  pollTimer = setInterval(() => {
    fetchMessages()
  }, 3000)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})
</script>

<template>
  <div class="alliance-chat-page">
    <div class="header">
      <span class="title">联盟聊天室</span>
      <a class="link-back" @click="goBack">回联盟</a>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    
    <div v-else class="chat-container" ref="chatContainer">
      <div v-if="messages.length === 0" class="empty-tip">暂无消息，快来聊聊吧！</div>
      <div v-for="msg in messages" :key="msg.id" class="message-item">
        <span class="time">[{{ msg.created_at }}]</span>
        <span class="nickname">{{ msg.nickname }}:</span>
        <span class="content">{{ msg.content }}</span>
      </div>
    </div>

    <div class="input-area">
      <input 
        v-model="newMessage" 
        type="text" 
        class="chat-input" 
        placeholder="说点什么..." 
        @keyup.enter="sendMessage"
      />
      <button class="send-btn" @click="sendMessage">发送</button>
    </div>
  </div>
</template>

<style scoped>
.alliance-chat-page {
  background: #FFF8DC;
  height: 100vh;
  display: flex;
  flex-direction: column;
  font-family: SimSun, "宋体", serif;
  font-size: 13px;
}

.header {
  background: #DEB887;
  padding: 8px 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #8B4513;
}

.title {
  font-weight: bold;
  color: #8B4513;
}

.link-back {
  color: #0066CC;
  cursor: pointer;
  text-decoration: none;
}

.chat-container {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  background: rgba(255, 255, 255, 0.3);
}

.message-item {
  margin-bottom: 6px;
  line-height: 1.4;
}

.time {
  color: #666;
  margin-right: 4px;
}

.nickname {
  color: #0066CC;
  font-weight: bold;
  margin-right: 4px;
}

.content {
  color: #333;
  word-break: break-all;
}

.input-area {
  padding: 10px;
  background: #DEB887;
  display: flex;
  gap: 8px;
}

.chat-input {
  flex: 1;
  padding: 6px;
  border: 1px solid #8B4513;
}

.send-btn {
  padding: 6px 15px;
  background: #8B4513;
  color: white;
  border: none;
  cursor: pointer;
}

.loading, .empty-tip {
  text-align: center;
  padding: 20px;
  color: #666;
}
</style>
