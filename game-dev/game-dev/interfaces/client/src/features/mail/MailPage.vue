<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import http from '@/services/http'

import { useToast } from '@/composables/useToast'
const { toast } = useToast()
const router = useRouter()
const route = useRoute()

const TAB_PM = 'pm'
const TAB_REQUEST = 'request'

const activeTab = ref(TAB_PM)

// 私信：给当前玩家发过消息的玩家
const pmSenders = ref([])
const loadingPm = ref(false)

// 请求：申请加当前玩家为好友的记录
const friendRequests = ref([])
const loadingRequest = ref(false)

// 分页
const pageSize = 10
const pmPage = ref(1)
const requestPage = ref(1)
const pageInput = ref('1')

const pmTotalPages = computed(() => Math.max(1, Math.ceil(pmSenders.value.length / pageSize)))
const requestTotalPages = ref(1)

const currentPage = computed(() => (activeTab.value === TAB_PM ? pmPage.value : requestPage.value))
const totalPages = computed(() => (activeTab.value === TAB_PM ? pmTotalPages.value : requestTotalPages.value))

const pmPageItems = computed(() => {
  const start = (pmPage.value - 1) * pageSize
  return pmSenders.value.slice(start, start + pageSize)
})

const requestPageItems = computed(() => {
  return friendRequests.value
})

const syncTabFromRoute = () => {
  const tab = String(route.query.tab || '')
  if (tab === TAB_REQUEST) {
    activeTab.value = TAB_REQUEST
  } else {
    activeTab.value = TAB_PM
  }
}

const selectTab = async (tab) => {
  activeTab.value = tab
  pageInput.value = '1'
  if (tab === TAB_PM) {
    pmPage.value = 1
    await loadPmSenders()
  } else {
    requestPage.value = 1
    await loadFriendRequests()
  }
  router.replace({ path: '/mail', query: { tab } })
}

const jumpToPage = async () => {
  const page = parseInt(pageInput.value, 10)
  if (!Number.isFinite(page)) return
  if (page < 1 || page > totalPages.value) return

  if (activeTab.value === TAB_PM) {
    pmPage.value = page
  } else {
    requestPage.value = page
    await loadFriendRequests()
  }
}

const goFirst = () => {
  if (activeTab.value === TAB_PM) pmPage.value = 1
  else requestPage.value = 1
}

const goPrev = () => {
  if (activeTab.value === TAB_PM) pmPage.value = Math.max(1, pmPage.value - 1)
  else requestPage.value = Math.max(1, requestPage.value - 1)
}

const goNext = async () => {
  if (activeTab.value === TAB_PM) {
    pmPage.value = Math.min(pmTotalPages.value, pmPage.value + 1)
  } else {
    requestPage.value = Math.min(requestTotalPages.value, requestPage.value + 1)
    await loadFriendRequests()
  }
}

const goLast = async () => {
  if (activeTab.value === TAB_PM) {
    pmPage.value = pmTotalPages.value
  } else {
    requestPage.value = requestTotalPages.value
    await loadFriendRequests()
  }
}

// 请求页：是否允许陌生人添加好友
const allowStrangerAdd = ref(true)
const loadingSetting = ref(false)

// 加载私信发送者列表
const loadPmSenders = async () => {
  loadingPm.value = true
  try {
    const res = await http.get('/mail/private-message/senders')
    if (res.data.ok) {
      pmSenders.value = res.data.senders || []
    } else {
      console.error('加载私信列表失败:', res.data.error)
    }
  } catch (e) {
    console.error('加载私信列表失败', e)
  } finally {
    loadingPm.value = false
  }
}

// 加载好友请求列表
const loadFriendRequests = async () => {
  loadingRequest.value = true
  try {
    const res = await http.get('/mail/friend-request/list', {
      params: {
        page: requestPage.value,
        page_size: pageSize
      }
    })
    if (res.data.ok) {
      friendRequests.value = res.data.requests || []
      requestTotalPages.value = res.data.total_pages || 1
    } else {
      console.error('加载好友请求列表失败:', res.data.error)
    }
  } catch (e) {
    console.error('加载好友请求列表失败', e)
  } finally {
    loadingRequest.value = false
  }
}

// 加载是否允许陌生人添加好友的设置
const loadAllowSetting = async () => {
  loadingSetting.value = true
  try {
    const res = await http.get('/mail/friend-request/setting')
    if (res.data.ok) {
      allowStrangerAdd.value = res.data.allow_stranger_add_friend !== false
    }
  } catch (e) {
    console.error('加载设置失败', e)
  } finally {
    loadingSetting.value = false
  }
}

// 切换是否允许陌生人添加好友
const toggleAllowStrangerAdd = async () => {
  const newValue = !allowStrangerAdd.value
  loadingSetting.value = true
  try {
    const res = await http.post('/mail/friend-request/setting', {
      allow: newValue
    })
    if (res.data.ok) {
      allowStrangerAdd.value = newValue
    } else {
      toast.error(res.data.error || '设置失败')
    }
  } catch (e) {
    console.error('保存设置失败', e)
    toast.error('保存设置失败')
  } finally {
    loadingSetting.value = false
  }
}

// 删除私信会话
const deletePmSender = async (senderId) => {
  if (!confirm('确定要删除与这个玩家的所有私信吗？')) {
    return
  }
  
  try {
    const res = await http.delete('/mail/private-message/conversation', {
      params: { target_id: senderId }
    })
    if (res.data.ok) {
      // 重新加载列表
      await loadPmSenders()
    } else {
      toast.error(res.data.error || '删除失败')
    }
  } catch (e) {
    console.error('删除私信失败', e)
    toast.error('删除失败')
  }
}

// 打开私信聊天
const openChat = (sender) => {
  router.push({
    path: '/mail/chat',
    query: {
      target_id: sender.user_id || sender.id,
      name: sender.name
    }
  })
}

const goHome = () => {
  router.push('/')
}

onMounted(async () => {
  syncTabFromRoute()
  await loadAllowSetting()
  if (activeTab.value === TAB_PM) {
    await loadPmSenders()
  } else {
    await loadFriendRequests()
  }
})

watch(
  () => route.query.tab,
  () => {
    syncTabFromRoute()
    // 切 tab 时重置输入框，避免“跳转”提示误导
    pageInput.value = String(currentPage.value || 1)
  },
)
</script>

<template>
  <div class="mail-page">
    <!-- 顶部 Tab：只实现 私信 / 请求（公告、系统不展示） -->
    <div class="section tabs">
      <a
        class="link"
        :class="{ active: activeTab === TAB_PM }"
        @click="selectTab(TAB_PM)"
      >私信</a>
      <span> | </span>
      <a
        class="link"
        :class="{ active: activeTab === TAB_REQUEST }"
        @click="selectTab(TAB_REQUEST)"
      >请求</a>
    </div>

    <!-- 私信列表 -->
    <template v-if="activeTab === TAB_PM">
      <div v-if="loadingPm" class="section gray">加载中...</div>
      <div v-else-if="pmSenders.length === 0" class="section gray">
        暂无私信
      </div>

      <div v-else>
        <div v-for="p in pmPageItems" :key="p.id || p.user_id" class="section row">
          <span class="name">
            <a class="link" @click="openChat(p)">{{ p.name }}</a>
          </span>
          <a class="link" @click="deletePmSender(p.user_id || p.id)">[删除]</a>
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
      <div v-if="loadingRequest" class="section gray">加载中...</div>
      <div v-else-if="friendRequests.length === 0" class="section gray">
        暂无好友请求
      </div>

      <div v-else>
        <div v-for="r in requestPageItems" :key="r.id" class="section request-row">
          <span class="time">({{ r.time }})</span>
          <a class="link" @click="() => {}">{{ r.from }}</a>
          <span>{{ r.text }}</span>
          <span v-if="r.status" class="gray">（{{ r.status }}）</span>
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
        <a class="link" @click="toggleAllowStrangerAdd" :class="{ disabled: loadingSetting }">
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

.section {
  margin: 2px 0;
}

.tabs {
  margin-bottom: 8px;
}

.row {
  display: flex;
  gap: 6px;
  align-items: center;
}

.name {
  flex: 0 0 auto;
}

.request-row {
  display: flex;
  gap: 6px;
  align-items: baseline;
  flex-wrap: wrap;
}

.time {
  color: #000;
}

.nav {
  margin-top: 8px;
}

.nav .link + .link {
  margin-left: 8px;
}

.pager {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
}

.page-input {
  width: 48px;
  height: 22px;
  padding: 0 6px;
  border: 1px solid #aaa;
}

.btn {
  height: 22px;
  padding: 0 8px;
  border: 1px solid #aaa;
  background: #f7f7f7;
  cursor: pointer;
}

.btn:hover {
  background: #eeeeee;
}

.back {
  margin-top: 12px;
}

.link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.link.active {
  color: #000;
  font-weight: bold;
  text-decoration: none;
  cursor: default;
}

.gray {
  color: #666666;
}

.link.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.small {
  font-size: 11px;
}

.footer {
  margin-top: 18px;
  padding-top: 10px;
  border-top: 1px solid #CCCCCC;
}
</style>
