<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()

const TAB_PM = 'pm'
const TAB_REQUEST = 'request'

const activeTab = ref(TAB_PM)
const loading = ref(false)

// 私信发送者列表
const pmSenders = ref([])

// 好友请求列表
const friendRequests = ref([])

// 分页
const pageSize = 10
const pmPage = ref(1)
const pmTotalPages = ref(1)
const requestPage = ref(1)
const requestTotalPages = ref(1)
const pageInput = ref('1')

const currentPage = computed(() => (activeTab.value === TAB_PM ? pmPage.value : requestPage.value))
const totalPages = computed(() => (activeTab.value === TAB_PM ? pmTotalPages.value : requestTotalPages.value))

// 加载私信发送者列表
const loadPmSenders = async () => {
  loading.value = true
  try {
    const res = await http.get('/mail/private-message/senders')
    if (res.data.ok) {
      pmSenders.value = res.data.senders || []
    }
  } catch (e) {
    console.error('加载私信列表失败', e)
  } finally {
    loading.value = false
  }
}

// 加载好友请求列表
const loadFriendRequests = async (page = 1) => {
  loading.value = true
  try {
    const res = await http.get('/mail/friend-request/list', { params: { page, page_size: pageSize } })
    if (res.data.ok) {
      friendRequests.value = res.data.requests || []
      requestPage.value = res.data.page || 1
      requestTotalPages.value = res.data.total_pages || 1
      pageInput.value = String(requestPage.value)
    }
  } catch (e) {
    console.error('加载好友请求失败', e)
  } finally {
    loading.value = false
  }
}

const syncTabFromRoute = () => {
  const tab = String(route.query.tab || '')
  if (tab === TAB_REQUEST) {
    activeTab.value = TAB_REQUEST
  } else {
    activeTab.value = TAB_PM
  }
}

const selectTab = (tab) => {
  activeTab.value = tab
  pageInput.value = '1'
  if (tab === TAB_PM) {
    pmPage.value = 1
    loadPmSenders()
  } else {
    requestPage.value = 1
    loadFriendRequests(1)
  }
  router.replace({ path: '/mail', query: { tab } })
}

const jumpToPage = () => {
  const page = parseInt(pageInput.value, 10)
  if (!Number.isFinite(page)) return
  if (page < 1 || page > totalPages.value) return

  if (activeTab.value === TAB_PM) {
    pmPage.value = page
  } else {
    requestPage.value = page
    loadFriendRequests(page)
  }
}

const goFirst = () => {
  if (activeTab.value === TAB_PM) pmPage.value = 1
  else loadFriendRequests(1)
}

const goPrev = () => {
  if (activeTab.value === TAB_PM) pmPage.value = Math.max(1, pmPage.value - 1)
  else loadFriendRequests(Math.max(1, requestPage.value - 1))
}

const goNext = () => {
  if (activeTab.value === TAB_PM) pmPage.value = Math.min(pmTotalPages.value, pmPage.value + 1)
  else loadFriendRequests(Math.min(requestTotalPages.value, requestPage.value + 1))
}

const goLast = () => {
  if (activeTab.value === TAB_PM) pmPage.value = pmTotalPages.value
  else loadFriendRequests(requestTotalPages.value)
}

// 删除私信会话
const deletePmSender = async (sender) => {
  if (!confirm(`确定删除与 ${sender.name} 的所有私信吗？`)) return
  try {
    const res = await http.delete('/mail/private-message/conversation', { params: { target_id: sender.user_id } })
    if (res.data.ok) {
      await loadPmSenders()
    } else {
      alert(res.data.error || '删除失败')
    }
  } catch (e) {
    alert(e?.response?.data?.error || '删除失败')
  }
}

// 打开私信聊天
const openChat = (sender) => {
  router.push({ path: '/mail/chat', query: { target_id: sender.user_id, name: sender.name } })
}

// 接受好友请求
const acceptRequest = async (req) => {
  try {
    const res = await http.post('/mail/friend-request/accept', { request_id: req.id })
    if (res.data.ok) {
      await loadFriendRequests(requestPage.value)
    } else {
      alert(res.data.error || '操作失败')
    }
  } catch (e) {
    alert(e?.response?.data?.error || '操作失败')
  }
}

// 拒绝好友请求
const rejectRequest = async (req) => {
  try {
    const res = await http.post('/mail/friend-request/reject', { request_id: req.id })
    if (res.data.ok) {
      await loadFriendRequests(requestPage.value)
    } else {
      alert(res.data.error || '操作失败')
    }
  } catch (e) {
    alert(e?.response?.data?.error || '操作失败')
  }
}

// 请求页：是否允许陌生人添加好友
const STORAGE_KEY_ALLOW_STRANGER = 'game_allow_stranger_add_friend'
const allowStrangerAdd = ref(true)

const loadAllowSetting = () => {
  const raw = localStorage.getItem(STORAGE_KEY_ALLOW_STRANGER)
  if (raw === '0') allowStrangerAdd.value = false
  if (raw === '1') allowStrangerAdd.value = true
}

const toggleAllowStrangerAdd = () => {
  allowStrangerAdd.value = !allowStrangerAdd.value
  localStorage.setItem(STORAGE_KEY_ALLOW_STRANGER, allowStrangerAdd.value ? '1' : '0')
}

const goHome = () => {
  router.push('/')
}

onMounted(async () => {
  syncTabFromRoute()
  loadAllowSetting()
  if (activeTab.value === TAB_PM) {
    await loadPmSenders()
  } else {
    await loadFriendRequests(1)
  }
})

watch(
  () => route.query.tab,
  () => {
    syncTabFromRoute()
    pageInput.value = String(currentPage.value || 1)
  },
)
</script>

<template>
  <div class="mail-page">
    <!-- 顶部 Tab -->
    <div class="section tabs">
      <a class="link" :class="{ active: activeTab === TAB_PM }" @click="selectTab(TAB_PM)">私信</a>
      <span> | </span>
      <a class="link" :class="{ active: activeTab === TAB_REQUEST }" @click="selectTab(TAB_REQUEST)">请求</a>
    </div>

    <!-- 私信列表 -->
    <template v-if="activeTab === TAB_PM">
      <div v-if="loading" class="section gray">加载中...</div>
      <div v-else-if="pmSenders.length === 0" class="section gray">暂无私信</div>
      <div v-else>
        <div v-for="p in pmSenders" :key="p.id" class="section row">
          <span class="name">
            <a class="link" @click="openChat(p)">{{ p.name }}</a>
            <span v-if="p.unread_count > 0" class="unread">({{ p.unread_count }}条未读)</span>
          </span>
          <a class="link" @click="deletePmSender(p)">[删除]</a>
        </div>
      </div>

      <div class="section pager">
        <span>{{ pmPage }}/{{ pmTotalPages }}页</span>
        <input class="page-input" v-model="pageInput" />
        <button class="btn" @click="jumpToPage">跳转</button>
      </div>
    </template>

    <!-- 请求列表 -->
    <template v-else>
      <div v-if="loading" class="section gray">加载中...</div>
      <div v-else-if="friendRequests.length === 0" class="section gray">暂无好友请求</div>
      <div v-else>
        <div v-for="r in friendRequests" :key="r.id" class="section request-row">
          <span class="time">({{ r.time }})</span>
          <a class="link" @click="router.push(`/player/profile?id=${r.requester_id}`)">{{ r.from }}</a>
          <span>{{ r.text }}</span>
          <template v-if="r.status">
            <span class="gray">（{{ r.status }}）</span>
          </template>
          <template v-else>
            <a class="link green" @click="acceptRequest(r)">[同意]</a>
            <a class="link red" @click="rejectRequest(r)">[拒绝]</a>
          </template>
        </div>
      </div>

      <div class="section nav">
        <template v-if="currentPage > 1">
          <a class="link" @click="goFirst">首页</a>
          <a class="link" @click="goPrev">上页</a>
        </template>
        <template v-if="currentPage < totalPages">
          <a class="link" @click="goNext">下页</a>
          <a class="link" @click="goLast">末页</a>
        </template>
      </div>

      <div class="section pager">
        <span>{{ requestPage }}/{{ requestTotalPages }}页</span>
        <input class="page-input" v-model="pageInput" />
        <button class="btn" @click="jumpToPage">跳转</button>
      </div>

      <div class="section">
        <a class="link" @click="toggleAllowStrangerAdd">
          <span v-if="allowStrangerAdd">拒绝陌生人添加好友 (已允许)</span>
          <span v-else>允许陌生人添加好友 (已拒绝)</span>
        </a>
      </div>
    </template>

    <div class="section back">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>
  </div>
</template>

<style scoped>
.mail-page {
  background: #FFF8DC;
  min-height: 100vh;
  padding: 12px;
  font-size: 13px;
  line-height: 1.7;
  font-family: SimSun, "宋体", serif;
}
.section { margin: 2px 0; }
.tabs { margin-bottom: 8px; }
.row { display: flex; gap: 6px; align-items: center; }
.name { flex: 0 0 auto; }
.unread { color: #CC0000; font-size: 12px; margin-left: 4px; }
.request-row { display: flex; gap: 6px; align-items: baseline; flex-wrap: wrap; }
.time { color: #000; }
.nav { margin-top: 8px; }
.nav .link + .link { margin-left: 8px; }
.pager { display: flex; align-items: center; gap: 6px; margin-top: 8px; }
.page-input { width: 48px; height: 22px; padding: 0 6px; border: 1px solid #aaa; }
.btn { height: 22px; padding: 0 8px; border: 1px solid #aaa; background: #f7f7f7; cursor: pointer; }
.btn:hover { background: #eeeeee; }
.back { margin-top: 12px; }
.link { color: #0066CC; cursor: pointer; text-decoration: none; }
.link:hover { text-decoration: underline; }
.link.active { color: #000; font-weight: bold; text-decoration: none; cursor: default; }
.link.green { color: #009900; }
.link.red { color: #CC0000; }
.gray { color: #666666; }
</style>
