<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const router = useRouter()
const route = useRoute()

const TAB_PM = 'pm'
const TAB_REQUEST = 'request'

const activeTab = ref(TAB_PM)

// 私信：给当前玩家发过消息的玩家（前端先用示例数据；后续可替换为接口数据）
const pmSenders = ref([
  { id: 1, name: '出号，出号' },
  { id: 2, name: 'AkenDa' },
  { id: 3, name: 'WorkingWrong' },
  { id: 4, name: '召唤之王888' },
  { id: 5, name: '—' },
  { id: 6, name: '茶哥。' },
  { id: 7, name: '派大星' },
])

// 请求：申请加当前玩家为好友的记录（前端先用示例数据；后续可替换为接口数据）
const friendRequests = ref([
  { id: 1, time: '12.12 14:44', from: '嘟嘟噜', text: '请求加你好友', status: '已同意' },
  { id: 2, time: '12.10 19:20', from: '小小怪', text: '请求加你好友', status: '已同意' },
  { id: 3, time: '12.10 08:17', from: '从来处来', text: '请求加你好友', status: '已同意' },
  { id: 4, time: '12.10 07:35', from: '暗河｜卡布奇诺', text: '通过了你的好友请求', status: '' },
  { id: 5, time: '12.10 01:09', from: '暗河变命师｜冷风', text: '请求加你好友', status: '已同意' },
  { id: 6, time: '12.09 18:30', from: '西北望，射天狼', text: '请求加你好友', status: '已同意' },
  { id: 7, time: '12.07 19:08', from: '暗河大家长｜山君', text: '请求加你好友', status: '已同意' },
  { id: 8, time: '12.07 00:18', from: '小琪々', text: '仰您的大名，请求拜您为师', status: '已同意' },
  { id: 9, time: '12.06 09:20', from: '茶哥。', text: '请求加你好友', status: '已同意' },
  { id: 10, time: '12.03 12:49', from: '橘子、', text: '请求加你好友', status: '已同意' },
])

// 分页
const pageSize = 10
const pmPage = ref(1)
const requestPage = ref(1)
const pageInput = ref('1')

const pmTotalPages = computed(() => Math.max(1, Math.ceil(pmSenders.value.length / pageSize)))
const requestTotalPages = computed(() => Math.max(1, Math.ceil(friendRequests.value.length / pageSize)))

const currentPage = computed(() => (activeTab.value === TAB_PM ? pmPage.value : requestPage.value))
const totalPages = computed(() => (activeTab.value === TAB_PM ? pmTotalPages.value : requestTotalPages.value))

const pmPageItems = computed(() => {
  const start = (pmPage.value - 1) * pageSize
  return pmSenders.value.slice(start, start + pageSize)
})

const requestPageItems = computed(() => {
  const start = (requestPage.value - 1) * pageSize
  return friendRequests.value.slice(start, start + pageSize)
})

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
  } else {
    requestPage.value = 1
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

const goNext = () => {
  if (activeTab.value === TAB_PM) pmPage.value = Math.min(pmTotalPages.value, pmPage.value + 1)
  else requestPage.value = Math.min(requestTotalPages.value, requestPage.value + 1)
}

const goLast = () => {
  if (activeTab.value === TAB_PM) pmPage.value = pmTotalPages.value
  else requestPage.value = requestTotalPages.value
}

// 删除（前端先做本地删除；后续可接接口）
const deletePmSender = (id) => {
  pmSenders.value = pmSenders.value.filter(x => x.id !== id)
  if (pmPage.value > pmTotalPages.value) pmPage.value = pmTotalPages.value
}

// 请求页：是否允许陌生人添加好友（前端先用 localStorage）
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

onMounted(() => {
  syncTabFromRoute()
  loadAllowSetting()
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
      <div v-if="pmSenders.length === 0" class="section gray">
        暂无私信
      </div>

      <div v-for="p in pmPageItems" :key="p.id" class="section row">
        <span class="name">
          <a class="link" @click="() => {}">{{ p.name }}</a>
        </span>
        <a class="link" @click="deletePmSender(p.id)">[删除]</a>
      </div>

      <div class="section pager">
        <span>{{ pmPage }}/{{ pmTotalPages }}页</span>
        <input class="page-input" v-model="pageInput" />
        <button class="btn" @click="jumpToPage">跳转</button>
      </div>
    </template>

    <!-- 请求列表 -->
    <template v-else>
      <div v-if="friendRequests.length === 0" class="section gray">
        暂无好友请求
      </div>

      <div v-for="r in requestPageItems" :key="r.id" class="section request-row">
        <span class="time">({{ r.time }})</span>
        <a class="link" @click="() => {}">{{ r.from }}</a>
        <span>{{ r.text }}</span>
        <span v-if="r.status" class="gray">（{{ r.status }}）</span>
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

.small {
  font-size: 11px;
}

.footer {
  margin-top: 18px;
  padding-top: 10px;
  border-top: 1px solid #CCCCCC;
}
</style>
