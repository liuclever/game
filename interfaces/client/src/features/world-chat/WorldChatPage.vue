<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()

const messages = ref([])
const pinnedMessage = ref(null)
const loading = ref(false)
const messageInput = ref('')
const sending = ref(false)
const currentPage = ref(1)
const totalPages = ref(1)
const pageInput = ref('1')
const hornCount = ref(0)
const isSummonKing = ref(false)

const loadMessages = async (page = 1) => {
  loading.value = true
  try {
    const res = await http.get('/world-chat/messages', { params: { page, page_size: 10 } })
    if (res.data.ok) {
      messages.value = res.data.messages || []
      currentPage.value = res.data.page || 1
      totalPages.value = res.data.total_pages || 1
      pageInput.value = String(currentPage.value)
    }
  } finally { loading.value = false }
}

const loadPinnedMessage = async () => {
  try {
    const res = await http.get('/world-chat/pinned')
    if (res.data.ok) pinnedMessage.value = res.data.message
  } catch (e) {}
}

const loadHornCount = async () => {
  try {
    const res = await http.get('/world-chat/horn-count')
    if (res.data.ok) hornCount.value = res.data.count || 0
  } catch (e) {}
}

const checkIsSummonKing = async () => {
  try {
    const res = await http.get('/world-chat/is-summon-king')
    if (res.data.ok) isSummonKing.value = res.data.is_summon_king || false
  } catch (e) {}
}

const sendMessage = async () => {
  if (!messageInput.value.trim()) { console.error('请输入消息内容'); return }
  if (messageInput.value.length > 35) { console.error('消息长度不能超过35个字符'); return }
  
  // 如果是召唤之王，发送置顶消息（不消耗小喇叭）
  // 否则发送普通消息（需要小喇叭）
  const messageType = isSummonKing.value ? 'summon_king' : 'normal'
  
  if (messageType === 'normal' && hornCount.value < 1) {
    console.error('小喇叭数量不足')
    return
  }
  
  sending.value = true
  try {
    const res = await http.post('/world-chat/send', { 
      content: messageInput.value.trim(), 
      message_type: messageType 
    })
    if (res.data.ok) {
      messageInput.value = ''
      await loadHornCount()
      await loadMessages(1)
      await loadPinnedMessage()  // 重新加载置顶消息（召唤之王发送新消息后会更新置顶）
    } else console.error(res.data.error || '发送失败')
  } catch (e) { console.error(e.response?.data?.error || '发送失败') }
  finally { sending.value = false }
}

const viewProfile = (msg) => { if (msg?.user_id) router.push(`/player/profile?id=${msg.user_id}`) }
const jumpToPage = () => {
  const page = parseInt(pageInput.value)
  if (page >= 1 && page <= totalPages.value) loadMessages(page)
  else { console.error(`请输入1-${totalPages.value}之间的页码`); pageInput.value = String(currentPage.value) }
}
const nextPage = () => { if (currentPage.value < totalPages.value) loadMessages(currentPage.value + 1) }
const lastPage = () => { loadMessages(totalPages.value) }
const goHome = () => { router.push('/') }

onMounted(async () => {
  await Promise.all([loadMessages(1), loadPinnedMessage(), loadHornCount(), checkIsSummonKing()])
})
</script>

<template>
  <div class="world-chat-page">
    <div class="section">每次发言需要一个喇叭(35字内)。</div>
    <div class="section input-section">
      <input v-model="messageInput" type="text" class="message-input" :maxlength="35" placeholder="请输入消息" @keyup.enter="sendMessage" />
      <button class="btn send-btn" @click="sendMessage" :disabled="sending">{{ sending ? '发送中...' : '发送' }}</button>
    </div>
    <div class="section">小喇叭×{{ hornCount }}.</div>
    <div class="section pinned-section" v-if="pinnedMessage">
      <div class="msg pinned clickable" @click="viewProfile(pinnedMessage)">({{ pinnedMessage.time }}) {{ pinnedMessage.nickname }}🏆：{{ pinnedMessage.content }}</div>
    </div>
    <div class="section messages-section">
      <div v-if="loading" class="msg">加载中...</div>
      <div v-for="msg in messages" :key="msg.id" class="msg clickable" @click="viewProfile(msg)">({{ msg.time }}) {{ msg.nickname }}🏆：{{ msg.content }}</div>
      <div v-if="!loading && messages.length === 0" class="msg gray">暂无消息</div>
    </div>
    <div class="section pager">
      <a class="link" @click="nextPage" v-if="currentPage < totalPages">下页</a>
      <a class="link" @click="lastPage" v-if="currentPage < totalPages">末页</a>
      <span>{{ currentPage }}/{{ totalPages }}页</span>
      <input v-model="pageInput" type="number" class="page-input" :min="1" :max="totalPages" />
      <button class="btn" @click="jumpToPage">跳转</button>
    </div>
    <div class="section"><a class="link" @click="goHome">返回游戏首页</a></div>
  </div>
</template>

<style scoped>
.world-chat-page { background: #ffffff; min-height: 100vh; padding: 8px 12px; font-size: 16px; line-height: 1.6; font-family: SimSun, "宋体", serif; }
.section { margin: 4px 0; }
.input-section { display: flex; gap: 4px; align-items: center; }
.message-input { flex: 1; padding: 4px 8px; border: 1px solid #ccc; font-size: 16px; }
.btn { padding: 4px 12px; background: #0066CC; color: white; border: 1px solid #0066CC; cursor: pointer; font-size: 16px; }
.btn:hover { background: #0052A3; }
.btn:disabled { background: #ffffff; cursor: not-allowed; }
.messages-section { border: 1px solid #ddd; padding: 8px; min-height: 200px; max-height: 400px; overflow-y: auto; }
.msg { margin: 2px 0; padding: 2px 0; }
.msg.pinned { background: #ffffff; padding: 6px 8px; border: 1px solid #FF6600; border-left: 4px solid #FF6600; font-weight: bold; }
.msg.clickable { cursor: pointer; padding: 2px 4px; border-radius: 2px; }
.msg.clickable:hover { background: #ffffff; }
.gray { color: #666; }
.pager { display: flex; gap: 8px; align-items: center; }
.page-input { width: 50px; padding: 2px 4px; border: 1px solid #ccc; text-align: center; }
.link { color: #0066CC; cursor: pointer; text-decoration: none; }
.link:hover { text-decoration: underline; }
</style>
