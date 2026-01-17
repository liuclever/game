<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const messages = ref([])
const newMessage = ref('')
const loading = ref(true)

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  try {
    const date = new Date(dateStr)
    const month = (date.getMonth() + 1).toString().padStart(2, '0')
    const day = date.getDate().toString().padStart(2, '0')
    const hours = date.getHours().toString().padStart(2, '0')
    const minutes = date.getMinutes().toString().padStart(2, '0')
    return `(${month}.${day} ${hours}:${minutes})`
  } catch (e) {
    return dateStr
  }
}

const fetchMessages = async () => {
  loading.value = true
  try {
    const res = await http.get('/alliance/chat/messages')
    if (res.data.ok) {
      messages.value = res.data.messages || []
    }
  } catch (e) {
    console.error('获取联盟消息失败', e)
    messages.value = []
  } finally {
    loading.value = false
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
      console.error(res.data.error || '发送失败')
    }
  } catch (e) {
    console.error(e.response?.data?.error || '发送失败')
  }
}

const refresh = () => {
  fetchMessages()
}

const goBack = () => {
  router.push('/alliance')
}

const goHome = () => {
  router.push('/')
}

onMounted(() => {
  fetchMessages()
})
</script>

<template>
  <div class="chat-page">
    <div class="section title">
      【聊天室】
      <a class="link" @click="refresh">刷新</a>
    </div>

    <div class="section input-area">
      <input 
        v-model="newMessage" 
        type="text" 
        class="input" 
        placeholder="说点什么..."
        @keyup.enter="sendMessage"
      />
      <button class="btn" @click="sendMessage">发送</button>
      <button class="btn">表情</button>
    </div>

    <div v-if="loading" class="section">加载中...</div>
    <div v-else-if="messages.length === 0" class="section">暂无消息,快来聊聊吧!</div>
    <div v-else class="section messages">
      <div v-for="msg in messages" :key="msg.id" class="message-item">
        {{ formatDate(msg.created_at) }} {{ msg.nickname }}: {{ msg.content }}
      </div>
    </div>

    <div class="section footer-links">
      <a class="link" @click="goBack">返回联盟</a>
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>
  </div>
</template>

<style scoped>
.chat-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 16px;
  line-height: 1.6;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 6px 0;
}

.title {
  font-weight: bold;
}

.link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: none;
  margin-left: 8px;
}

.link:hover:not(.disabled) {
  text-decoration: underline;
}

.link.disabled {
  color: #999;
  cursor: not-allowed;
}

.input-area {
  display: flex;
  gap: 8px;
  align-items: center;
}

.input {
  flex: 1;
  padding: 4px 8px;
  border: 1px solid #ccc;
  font-family: inherit;
  font-size: inherit;
}

.btn {
  padding: 4px 12px;
  border: 1px solid #ccc;
  background: #fff;
  cursor: pointer;
  font-family: inherit;
  font-size: inherit;
}

.btn:hover {
  background: #ffffff;
}

.messages {
  min-height: 200px;
}

.message-item {
  margin: 2px 0;
}

.footer-links {
  margin-top: 16px;
}

.footer-links .link {
  margin-right: 12px;
}
</style>
