<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

import { useToast } from '@/composables/useToast'
const { toast } = useToast()
const router = useRouter()

// 消息列表
const messages = ref([])
const pinnedMessage = ref(null)  // 置顶消息（召唤之王）
const loading = ref(false)

// 发送消息
const messageInput = ref('')
const sending = ref(false)

// 分页
const currentPage = ref(1)
const totalPages = ref(1)
const pageInput = ref('1')
const pageSize = 10

// 小喇叭数量
const hornCount = ref(0)

// 是否是召唤之王
const isSummonKing = ref(false)

// 当前登录用户ID
const currentUserId = ref(null)

// 加载消息列表（排除置顶消息，因为置顶消息单独显示）
const loadMessages = async (page = 1) => {
  loading.value = true
  try {
    const res = await http.get('/world-chat/messages', {
      params: { page, page_size: pageSize }
    })
    if (res.data.ok) {
      // 过滤掉置顶消息（因为置顶消息单独显示）
      const allMessages = res.data.messages || []
      messages.value = allMessages.filter(msg => !msg.is_pinned)
      currentPage.value = res.data.page || 1
      totalPages.value = res.data.total_pages || 1
      pageInput.value = String(currentPage.value)
    }
  } catch (e) {
    console.error('加载消息失败', e)
  } finally {
    loading.value = false
  }
}

// 加载置顶消息
const loadPinnedMessage = async () => {
  try {
    const res = await http.get('/world-chat/pinned')
    if (res.data.ok && res.data.message) {
      pinnedMessage.value = res.data.message
    }
  } catch (e) {
    console.error('加载置顶消息失败', e)
  }
}

// 加载小喇叭数量
const loadHornCount = async () => {
  try {
    const res = await http.get('/world-chat/horn-count')
    if (res.data.ok) {
      hornCount.value = res.data.count || 0
    }
  } catch (e) {
    console.error('加载小喇叭数量失败', e)
  }
}

// 检查是否是召唤之王
const checkIsSummonKing = async () => {
  try {
    const res = await http.get('/world-chat/is-summon-king')
    if (res.data.ok) {
      isSummonKing.value = res.data.is_summon_king || false
    }
  } catch (e) {
    console.error('检查召唤之王状态失败', e)
  }
}

// 获取当前登录用户ID
const loadCurrentUserId = async () => {
  try {
    const res = await http.get('/auth/status')
    if (res.data.logged_in) {
      currentUserId.value = res.data.user_id
    }
  } catch (e) {
    console.error('获取当前用户ID失败', e)
  }
}

// 点击消息，跳转到个人界面
const viewPlayerProfile = (msg) => {
  if (!msg || !msg.user_id) {
    return
  }
  
  // 判断是否是自己
  if (currentUserId.value && msg.user_id === currentUserId.value) {
    // 是自己的消息，跳转到自己的个人界面
    router.push(`/player/profile?id=${msg.user_id}`)
  } else {
    // 是其他人的消息，跳转到其他人的个人界面
    router.push(`/player/profile?id=${msg.user_id}`)
  }
}

// 发送普通消息
const sendNormalMessage = async () => {
  if (!messageInput.value.trim()) {
    toast.error('请输入消息内容')
    return
  }
  
  if (messageInput.value.length > 35) {
    toast.error('消息长度不能超过35个字符')
    return
  }
  
  if (hornCount.value < 1) {
    toast.error('小喇叭数量不足')
    return
  }
  
  sending.value = true
  try {
    const res = await http.post('/world-chat/send', {
      content: messageInput.value.trim(),
      message_type: 'normal'
    })
    if (res.data.ok) {
      messageInput.value = ''
      await loadHornCount()
      // 如果当前在第一页，刷新第一页；否则跳转到第一页
      if (currentPage.value === 1) {
        await loadMessages(1)
      } else {
        currentPage.value = 1
        await loadMessages(1)
      }
    } else {
      toast.error(res.data.error || '发送失败')
    }
  } catch (e) {
    console.error('发送消息失败:', e)
    const errorMsg = e.response?.data?.error || e.message || '发送失败'
    toast.error(errorMsg)
  } finally {
    sending.value = false
  }
}

// 发送召唤之王置顶消息
const sendSummonKingMessage = async () => {
  if (!messageInput.value.trim()) {
    toast.error('请输入消息内容')
    return
  }
  
  if (messageInput.value.length > 35) {
    toast.error('消息长度不能超过35个字符')
    return
  }
  
  if (!isSummonKing.value) {
    toast.error('只有召唤之王才能发布置顶消息')
    return
  }
  
  sending.value = true
  try {
    const res = await http.post('/world-chat/send', {
      content: messageInput.value.trim(),
      message_type: 'summon_king'
    })
    if (res.data.ok) {
      messageInput.value = ''
      // 刷新置顶消息
      await loadPinnedMessage()
      // 刷新第一页消息（因为新消息在第一页）
      if (currentPage.value === 1) {
        await loadMessages(1)
      } else {
        currentPage.value = 1
        await loadMessages(1)
      }
    } else {
      toast.error(res.data.error || '发送失败')
    }
  } catch (e) {
    console.error('发送召唤之王消息失败:', e)
    const errorMsg = e.response?.data?.error || e.message || '发送失败'
    toast.error(errorMsg)
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

// 返回首页
const goHome = () => {
  router.push('/')
}


onMounted(async () => {
  await Promise.all([
    loadMessages(1),
    loadPinnedMessage(),
    loadHornCount(),
    checkIsSummonKing(),
    loadCurrentUserId()
  ])
})
</script>

<template>
  <div class="world-chat-page">
    <div class="section">
      每次发言需要一个喇叭(35字内)。
    </div>
    
    <!-- 输入区域 -->
    <div class="section input-section">
      <input 
        v-model="messageInput" 
        type="text" 
        class="message-input"
        :maxlength="35"
        placeholder="请输入消息"
        @keyup.enter="sendNormalMessage"
      />
      <button class="btn send-btn" @click="sendNormalMessage" :disabled="sending">
        {{ sending ? '发送中...' : '发送' }}
      </button>
      <button class="btn emoji-btn">表情</button>
    </div>
    
    <!-- 小喇叭数量 -->
    <div class="section">
      小喇叭×{{ hornCount }}.
    </div>
    
    <!-- 召唤之王按钮（仅召唤之王可见） -->
    <div class="section" v-if="isSummonKing">
      <button class="btn summon-king-btn" @click="sendSummonKingMessage" :disabled="sending">
        【召唤之王】
      </button>
    </div>
    
    <!-- 置顶消息（召唤之王）- 单独显示在最顶部 -->
    <div class="section pinned-section" v-if="pinnedMessage">
      <div 
        class="msg pinned clickable" 
        @click="viewPlayerProfile(pinnedMessage)"
        :title="currentUserId && pinnedMessage.user_id === currentUserId ? '点击查看我的个人界面' : '点击查看玩家个人界面'"
      >
        ({{ pinnedMessage.time }}) {{ pinnedMessage.nickname }}🏆：{{ pinnedMessage.content }}
      </div>
    </div>
    
    <!-- 普通消息列表（不包含置顶消息，置顶消息已单独显示） -->
    <div class="section messages-section">
      <div v-if="loading" class="msg">加载中...</div>
      <div 
        v-for="msg in messages" 
        :key="msg.id" 
        class="msg clickable"
        @click="viewPlayerProfile(msg)"
        :title="currentUserId && msg.user_id === currentUserId ? '点击查看我的个人界面' : '点击查看玩家个人界面'"
      >
        ({{ msg.time }}) {{ msg.nickname }}🏆：{{ msg.content }}
      </div>
      <div v-if="!loading && messages.length === 0 && !pinnedMessage" class="msg gray">
        暂无消息
      </div>
      <div v-if="!loading && messages.length === 0 && pinnedMessage" class="msg gray">
        暂无普通消息
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
    
    <!-- 返回首页 -->
    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>
  </div>
</template>

<style scoped>
.world-chat-page {
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

.input-section {
  display: flex;
  gap: 4px;
  align-items: center;
}

.message-input {
  flex: 1;
  padding: 4px 8px;
  border: 1px solid #ccc;
  font-size: 13px;
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

.btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.send-btn {
  background: #0066CC;
}

.emoji-btn {
  background: #999;
}

.summon-king-btn {
  background: #FF6600;
  border-color: #FF6600;
}

.summon-king-btn:hover {
  background: #E55A00;
}

.messages-section {
  border: 1px solid #ddd;
  padding: 8px;
  min-height: 200px;
  max-height: 400px;
  overflow-y: auto;
}

.msg {
  margin: 2px 0;
  padding: 2px 0;
}

.pinned-section {
  margin-bottom: 8px;
}

.msg.pinned {
  background: #FFFACD;
  padding: 6px 8px;
  border: 1px solid #FF6600;
  border-left: 4px solid #FF6600;
  font-weight: bold;
}

.gray {
  color: #666;
}

.msg.clickable {
  cursor: pointer;
  padding: 2px 4px;
  border-radius: 2px;
  transition: background-color 0.2s;
}

.msg.clickable:hover {
  background-color: #f0f0f0;
}

.pager {
  display: flex;
  gap: 8px;
  align-items: center;
}

.page-input {
  width: 50px;
  padding: 2px 4px;
  border: 1px solid #ccc;
  text-align: center;
}

.link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}
</style>
