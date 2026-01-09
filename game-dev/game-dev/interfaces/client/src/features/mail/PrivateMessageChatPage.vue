<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

import { useToast } from '@/composables/useToast'
const { toast } = useToast()
const router = useRouter()
const route = useRoute()

// 目标用户信息
const targetUserId = ref(null)
const targetUserName = ref('')
const currentUserId = ref(null)

// 消息列表
const messages = ref([])
const loading = ref(false)

// 发送消息
const messageInput = ref('')
const sending = ref(false)

// 分页
const currentPage = ref(1)
const totalPages = ref(1)
const pageInput = ref('1')
const pageSize = 20

// 加载当前用户ID
const loadCurrentUserId = async () => {
  try {
    const res = await http.get('/auth/status')
    if (res.data.ok && res.data.user) {
      currentUserId.value = res.data.user.userId
    }
  } catch (e) {
    console.error('获取当前用户ID失败', e)
  }
}

// 加载聊天记录
const loadMessages = async (page = 1) => {
  if (!targetUserId.value) return
  
  loading.value = true
  try {
    const res = await http.get('/mail/private-message/conversation', {
      params: {
        target_id: targetUserId.value,
        page: page,
        page_size: pageSize
      }
    })
    
    if (res.data.ok) {
      messages.value = res.data.messages || []
      currentPage.value = res.data.page || 1
      totalPages.value = res.data.total_pages || 1
      pageInput.value = String(currentPage.value)
    } else {
      toast.error(res.data.error || '加载失败')
    }
  } catch (e) {
    console.error('加载聊天记录失败', e)
    toast.error('加载失败')
  } finally {
    loading.value = false
  }
}

// 发送消息
const sendMessage = async () => {
  if (!messageInput.value.trim() || sending.value) return
  
  const content = messageInput.value.trim()
  if (content.length > 30) {
    toast.error('消息内容不能超过30字')
    return
  }
  
  sending.value = true
  try {
    const res = await http.post('/mail/private-message/send', {
      target_id: targetUserId.value,
      content: content
    })
    
    if (res.data.ok) {
      messageInput.value = ''
      // 重新加载消息（从第一页开始）
      await loadMessages(1)
    } else {
      toast.error(res.data.error || '发送失败')
    }
  } catch (e) {
    console.error('发送消息失败', e)
    toast.error(e?.response?.data?.error || '发送失败')
  } finally {
    sending.value = false
  }
}

// 分页跳转
const jumpToPage = () => {
  const page = parseInt(pageInput.value)
  if (page >= 1 && page <= totalPages.value) {
    loadMessages(page)
  } else {
    toast.error(`请输入1-${totalPages.value}之间的页码`)
    pageInput.value = String(currentPage.value)
  }
}

// 下一页
const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    loadMessages(currentPage.value + 1)
  }
}

// 末页
const lastPage = () => {
  loadMessages(totalPages.value)
}

// 返回前页
const goBack = () => {
  router.back()
}

onMounted(async () => {
  await loadCurrentUserId()
  
  const targetId = route.query.target_id || route.query.id
  if (targetId) {
    targetUserId.value = parseInt(targetId)
    targetUserName.value = route.query.name || `玩家${targetId}`
    await loadMessages(1)
  } else {
    toast.error('缺少目标用户ID')
    router.back()
  }
})
</script>

<template>
  <div class="chat-page">
    <div class="section title">
      给[{{ targetUserName }}]发送短信（30字内）:
    </div>
    
    <!-- 发送消息区域 -->
    <div class="section send-area">
      <input 
        v-model="messageInput" 
        type="text" 
        class="message-input"
        :maxlength="30"
        placeholder="输入消息内容（最多30字）"
        @keyup.enter="sendMessage"
      />
      <button 
        class="btn send-btn" 
        @click="sendMessage"
        :disabled="sending || !messageInput.trim()"
      >
        发送
      </button>
    </div>
    
    <!-- 历史消息 -->
    <div class="section title2">历史消息：</div>
    
    <div v-if="loading" class="section gray">加载中...</div>
    <div v-else-if="messages.length === 0" class="section gray">暂无消息</div>
    <div v-else class="messages-list">
      <div 
        v-for="msg in messages" 
        :key="msg.id" 
        class="section message-item"
      >
        <span class="time">({{ msg.time }})</span>
        <span v-if="msg.is_me" class="sender me">我:</span>
        <span v-else class="sender">{{ msg.sender_name }}:</span>
        <span class="content">{{ msg.content }}</span>
      </div>
    </div>
    
    <!-- 分页控件 -->
    <div class="section pager">
      <a class="link" @click="nextPage" v-if="currentPage < totalPages">下页</a>
      <a class="link" @click="lastPage" v-if="currentPage < totalPages">末页</a>
      <span>{{ currentPage }}/{{ totalPages }}页</span>
      <input 
        v-model="pageInput" 
        type="number" 
        class="page-input"
        :min="1"
        :max="totalPages"
      />
      <button class="btn" @click="jumpToPage">跳转</button>
    </div>
    
    <!-- 返回 -->
    <div class="section">
      <a class="link" @click="goBack">返回前页</a>
    </div>
  </div>
</template>

<style scoped>
.chat-page {
  background: #FFF8DC;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 13px;
  line-height: 1.6;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 4px 0;
}

.title {
  font-weight: bold;
  margin-bottom: 8px;
}

.title2 {
  font-weight: bold;
  margin-top: 12px;
  margin-bottom: 8px;
}

.send-area {
  display: flex;
  gap: 8px;
  align-items: center;
  margin: 8px 0;
}

.message-input {
  flex: 1;
  padding: 4px 8px;
  border: 1px solid #ccc;
  font-size: 13px;
}

.send-btn {
  padding: 4px 16px;
  background: #0066CC;
  color: white;
  border: 1px solid #0066CC;
  cursor: pointer;
  font-size: 13px;
}

.send-btn:hover:not(:disabled) {
  background: #0052A3;
}

.send-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.messages-list {
  border: 1px solid #ddd;
  padding: 8px;
  min-height: 200px;
  max-height: 400px;
  overflow-y: auto;
}

.message-item {
  margin: 4px 0;
  padding: 2px 0;
}

.time {
  color: #666;
  margin-right: 4px;
}

.sender {
  font-weight: bold;
  margin-right: 4px;
}

.sender.me {
  color: #0066CC;
}

.content {
  color: #000;
}

.pager {
  display: flex;
  gap: 8px;
  align-items: center;
  justify-content: center;
  margin: 8px 0;
}

.page-input {
  width: 50px;
  padding: 2px 4px;
  border: 1px solid #ccc;
  text-align: center;
}

.btn {
  padding: 4px 12px;
  background: #0066CC;
  color: white;
  border: 1px solid #0066CC;
  cursor: pointer;
  font-size: 13px;
}

.btn:hover {
  background: #0052A3;
}

.link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.gray {
  color: #666666;
}
</style>
