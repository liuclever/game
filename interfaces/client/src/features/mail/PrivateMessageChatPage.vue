<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'
import { useToast } from '@/composables/useToast'

const { toast } = useToast()
const router = useRouter()
const route = useRoute()

const targetUserId = ref(null)
const targetUserName = ref('')
const messages = ref([])
const loading = ref(false)
const messageInput = ref('')
const sending = ref(false)
const currentPage = ref(1)
const totalPages = ref(1)
const pageInput = ref('1')

const loadMessages = async (page = 1) => {
  if (!targetUserId.value) return
  loading.value = true
  try {
    const res = await http.get('/mail/private-message/conversation', {
      params: { target_id: targetUserId.value, page, page_size: 20 }
    })
    if (res.data.ok) {
      messages.value = res.data.messages || []
      currentPage.value = res.data.page || 1
      totalPages.value = res.data.total_pages || 1
      pageInput.value = String(currentPage.value)
    } else toast.error(res.data.error || '加载失败')
  } finally { loading.value = false }
}

const sendMessage = async () => {
  if (!messageInput.value.trim() || sending.value) return
  const content = messageInput.value.trim()
  if (content.length > 30) { toast.error('消息内容不能超过30字'); return }
  
  sending.value = true
  try {
    const res = await http.post('/mail/private-message/send', { target_id: targetUserId.value, content })
    if (res.data.ok) { messageInput.value = ''; await loadMessages(1) }
    else toast.error(res.data.error || '发送失败')
  } catch (e) { toast.error(e?.response?.data?.error || '发送失败') }
  finally { sending.value = false }
}

const jumpToPage = () => {
  const page = parseInt(pageInput.value)
  if (page >= 1 && page <= totalPages.value) loadMessages(page)
  else pageInput.value = String(currentPage.value)
}
const nextPage = () => { if (currentPage.value < totalPages.value) loadMessages(currentPage.value + 1) }
const lastPage = () => { loadMessages(totalPages.value) }
const goBack = () => { router.back() }

onMounted(async () => {
  const targetId = route.query.target_id || route.query.id
  if (targetId) {
    targetUserId.value = parseInt(targetId)
    targetUserName.value = route.query.name || `玩家${targetId}`
    await loadMessages(1)
  } else { toast.error('缺少目标用户ID'); router.back() }
})
</script>

<template>
  <div class="chat-page">
    <div class="section title">给[{{ targetUserName }}]发送短信（30字内）:</div>
    <div class="section send-area">
      <input v-model="messageInput" type="text" class="message-input" :maxlength="30" placeholder="输入消息内容（最多30字）" @keyup.enter="sendMessage" />
      <button class="btn send-btn" @click="sendMessage" :disabled="sending || !messageInput.trim()">发送</button>
    </div>
    <div class="section title2">历史消息：</div>
    <div v-if="loading" class="section gray">加载中...</div>
    <div v-else-if="messages.length === 0" class="section gray">暂无消息</div>
    <div v-else class="messages-list">
      <div v-for="msg in messages" :key="msg.id" class="section message-item">
        <span class="time">({{ msg.time }})</span>
        <span v-if="msg.is_me" class="sender me">我:</span>
        <span v-else class="sender">{{ msg.sender_name }}:</span>
        <span class="content">{{ msg.content }}</span>
      </div>
    </div>
    <div class="section pager">
      <a class="link" @click="nextPage" v-if="currentPage < totalPages">下页</a>
      <a class="link" @click="lastPage" v-if="currentPage < totalPages">末页</a>
      <span>{{ currentPage }}/{{ totalPages }}页</span>
      <input v-model="pageInput" type="number" class="page-input" />
      <button class="btn" @click="jumpToPage">跳转</button>
    </div>
    <div class="section"><a class="link" @click="goBack">返回前页</a></div>
  </div>
</template>

<style scoped>
.chat-page { background: #ffffff; min-height: 100vh; padding: 8px 12px; font-size: 16px; line-height: 1.6; font-family: SimSun, "宋体", serif; }
.section { margin: 4px 0; }
.title, .title2 { font-weight: bold; margin-bottom: 8px; }
.send-area { display: flex; gap: 8px; align-items: center; margin: 8px 0; }
.message-input { flex: 1; padding: 4px 8px; border: 1px solid #ccc; font-size: 16px; }
.send-btn { padding: 4px 16px; background: #0066CC; color: white; border: 1px solid #0066CC; cursor: pointer; font-size: 16px; }
.send-btn:disabled { background: #ffffff; cursor: not-allowed; }
.messages-list { border: 1px solid #ddd; padding: 8px; min-height: 200px; max-height: 400px; overflow-y: auto; }
.message-item { margin: 4px 0; padding: 2px 0; }
.time { color: #666; margin-right: 4px; }
.sender { font-weight: bold; margin-right: 4px; }
.sender.me { color: #0066CC; }
.pager { display: flex; gap: 8px; align-items: center; justify-content: center; margin: 8px 0; }
.page-input { width: 50px; padding: 2px 4px; border: 1px solid #ccc; text-align: center; }
.btn { padding: 4px 12px; background: #0066CC; color: white; border: 1px solid #0066CC; cursor: pointer; font-size: 16px; }
.link { color: #0066CC; cursor: pointer; }
.link:hover { text-decoration: underline; }
.gray { color: #666666; }
</style>
