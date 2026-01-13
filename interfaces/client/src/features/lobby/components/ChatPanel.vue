<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const messages = ref([])
const pinnedMessage = ref(null)
const currentUserId = ref(null)

// 加载首页消息（只显示3条普通喊话）
const loadHomepageMessages = async () => {
  try {
    // 加载置顶消息
    const pinnedRes = await http.get('/world-chat/pinned')
    if (pinnedRes.data.ok && pinnedRes.data.message) {
      pinnedMessage.value = pinnedRes.data.message
    }
    
    // 加载普通喊话（最多3条）
    const res = await http.get('/world-chat/homepage')
    if (res.data.ok) {
      messages.value = res.data.messages || []
    }
  } catch (e) {
    console.error('加载首页消息失败', e)
  }
}

// 跳转到世界聊天页面
const goToWorldChat = () => {
  router.push('/world-chat')
}

// 跳转到信件页面
const goToMail = () => {
  router.push('/mail')
}

// 跳转到动态页面
const goToDynamics = () => {
  router.push('/dynamics')
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
  
  // 跳转到个人界面（无论是自己还是其他人，都使用相同的路由）
  router.push(`/player/profile?id=${msg.user_id}`)
}

onMounted(() => {
  loadCurrentUserId()
  loadHomepageMessages()
  // 每5秒刷新一次消息
  setInterval(loadHomepageMessages, 5000)
})
</script>

<template>
  <div class="panel">
    <div class="tabs">
      <span class="link" @click="goToWorldChat">[世界]</span>
      <span class="link" @click="goToDynamics">[动态]</span>
      <span class="link" @click="goToMail">[信件]</span>
    </div>
    <div class="messages">
      <!-- 置顶消息（召唤之王） -->
      <div 
        class="msg pinned clickable" 
        v-if="pinnedMessage"
        @click="viewPlayerProfile(pinnedMessage)"
        :title="currentUserId && pinnedMessage.user_id === currentUserId ? '点击查看我的个人界面' : '点击查看玩家个人界面'"
      >
        【召唤之王】({{ pinnedMessage.time }}) {{ pinnedMessage.nickname }}🏆：{{ pinnedMessage.content }}
      </div>
      <!-- 普通喊话（最多3条） -->
      <div 
        v-for="msg in messages.slice(0, 3)" 
        :key="msg.id" 
        class="msg clickable"
        @click="viewPlayerProfile(msg)"
        :title="currentUserId && msg.user_id === currentUserId ? '点击查看我的个人界面' : '点击查看玩家个人界面'"
      >
        【喊话】({{ msg.time }}) {{ msg.nickname }}🏆：{{ msg.content }}
      </div>
      <div v-if="messages.length === 0 && !pinnedMessage" class="msg gray">
        暂无消息
      </div>
    </div>
  </div>
</template>

<style scoped>
.panel {
  border: 1px solid #dddddd;
  padding: 4px 8px;
}

.tabs {
  margin-bottom: 4px;
}

.link {
  color: #0033cc;
  cursor: pointer;
  margin-right: 4px;
}

.messages {
  max-height: 220px;
  overflow-y: auto;
}

.msg + .msg {
  margin-top: 2px;
}

.msg.pinned {
  background: #FFFACD;
  padding: 4px;
  border-left: 3px solid #FF6600;
  margin-bottom: 4px;
}

.msg.gray {
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
</style>
