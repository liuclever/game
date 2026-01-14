<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const router = useRouter()
const route = useRoute()

const TAB_LEVEL = 'level'
const TAB_SOCIAL = 'social'

const activeTab = ref(TAB_LEVEL)

// 当前玩家好友（前端先用示例数据；后续可替换为接口数据）
const friends = ref([
 
])

const sortedFriends = computed(() => {
  const list = [...friends.value]
  // 等级排行：按等级从高到低；同等级按昵称
  list.sort((a, b) => {
    const dl = (b.level || 0) - (a.level || 0)
    if (dl !== 0) return dl
    return String(a.nickname || '').localeCompare(String(b.nickname || ''))
  })
  return list
})

// 分页
const pageSize = 10
const currentPage = ref(1)
const totalPages = computed(() => Math.max(1, Math.ceil(sortedFriends.value.length / pageSize)))
const pageInput = ref('1')

const pageItems = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return sortedFriends.value.slice(start, start + pageSize)
})

const syncFromRoute = () => {
  const tab = String(route.query.tab || '')
  activeTab.value = tab === TAB_SOCIAL ? TAB_SOCIAL : TAB_LEVEL

  const p = parseInt(String(route.query.page || '1'), 10)
  currentPage.value = Number.isFinite(p) ? Math.min(Math.max(1, p), totalPages.value) : 1
  pageInput.value = String(currentPage.value)
}

const selectTab = (tab) => {
  activeTab.value = tab
  currentPage.value = 1
  pageInput.value = '1'
  router.replace({ path: '/friend', query: { tab } })
}

const goToPage = (page) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  pageInput.value = String(page)
  router.replace({ path: '/friend', query: { tab: activeTab.value, page } })
}

const jumpToPage = () => {
  const page = parseInt(pageInput.value, 10)
  if (!Number.isFinite(page)) return
  goToPage(page)
}

const spar = (f) => {
  alert(`切磋：${f.nickname}`)
}

const infuse = (f) => {
  alert(`灌注：${f.nickname}`)
}

const searchFriend = () => {
  router.push('/friend/search')
}

const openBlacklist = () => {
  alert('黑名单：暂未实现')
}

const goHome = () => {
  router.push('/')
}

// 复用简单导航（和其他页面一致）
const handleLink = (name) => {
  const routes = {
    '背包': '/inventory',
    '幻兽': '/beast',
    '地图': '/map',
    '擂台': '/arena',
    '闯塔': '/tower',
    '排行': '/ranking',
    '召唤之王挑战赛': '/king',
    '商城': '/shop',
    '战场': '/battlefield',
    '竞技': '/pvp',
    '化仙': '/huaxian',
    '信件': '/mail',
    '兑换': '/exchange',
    'VIP': '/vip',
    '提升': '/vip',
    '活力': '/vip',
    '图鉴': '/handbook',
  }
  if (routes[name]) {
    router.push(routes[name])
  } else {
    alert(`点击了: ${name}`)
  }
}

onMounted(() => {
  syncFromRoute()
})

watch(
  () => [route.query.tab, route.query.page],
  () => {
    syncFromRoute()
  },
)
</script>

<template>
  <div class="friend-page">
    <div class="section title">【我的好友】</div>

    <div class="section tabs">
      <a
        class="link"
        :class="{ active: activeTab === TAB_LEVEL }"
        @click="selectTab(TAB_LEVEL)"
      >等级排行</a>
      <span> | </span>
      <a
        class="link"
        :class="{ active: activeTab === TAB_SOCIAL }"
        @click="selectTab(TAB_SOCIAL)"
      >社交排行</a>
    </div>

    <template v-if="activeTab === TAB_LEVEL">
      <div v-for="(f, idx) in pageItems" :key="f.id" class="section item">
        <span class="rank">{{ (currentPage - 1) * pageSize + idx + 1 }}.</span>
        <span class="paren">(</span><span class="rank-name">{{ f.rank_name }}</span><span class="paren">)</span>
        <a class="link name" :class="{ red: f.highlight }" @click="() => {}">{{ f.nickname }}</a>
        <span class="vip">V{{ f.vip }}</span>
        <span class="level">({{ f.level }}级)</span>
        <span class="link readonly">切磋</span>
        <template v-if="f.can_infuse">
          <span> . </span>
          <a class="link" @click="infuse(f)">灌注</a>
        </template>
      </div>

      <!-- 分页（样式按截图：只显示 下页/末页，其他页显示 首页/上页） -->
      <div class="section pager-links">
        <a class="link" @click="goToPage(1)" v-if="currentPage > 1">首页</a>
        <a class="link" @click="goToPage(currentPage - 1)" v-if="currentPage > 1">上页</a>
        <a class="link" @click="goToPage(currentPage + 1)" v-if="currentPage < totalPages">下页</a>
        <a class="link" @click="goToPage(totalPages)" v-if="currentPage < totalPages">末页</a>
      </div>

      <div class="section pager">
        {{ currentPage }}/{{ totalPages }}页
        <input class="page-input" v-model="pageInput" />
        <button class="btn" @click="jumpToPage">跳转</button>
      </div>

      <div class="section">
        <a class="link" @click="searchFriend">查找好友</a>
        <a class="link" @click="openBlacklist" style="margin-left: 10px;">黑名单</a>
      </div>
    </template>

    <template v-else>
      <div class="section gray">社交排行：暂未实现</div>
    </template>

    <!-- 导航菜单（与截图一致的几行） -->
    <div class="section nav">
      皇城:<span class="link readonly">召唤之王挑战赛</span>
    </div>
    <div class="section nav">
      <a class="link" @click="handleLink('幻兽')">幻兽</a>. <a class="link" @click="handleLink('背包')">背包</a>.
      <a class="link" @click="handleLink('商城')">商城</a>. <a class="link" @click="handleLink('赞助')">赞助</a>. <a class="link" @click="handleLink('礼包')">礼包</a>
    </div>
    <div class="section nav">
      <a class="link" @click="handleLink('联盟')">联盟</a>. <a class="link" @click="handleLink('盟战')">盟战</a>.
      <a class="link" @click="handleLink('地图')">地图</a>. <span class="link readonly">天赋</span>. <a class="link" @click="handleLink('化仙')">化仙</a>
    </div>
    <div class="section nav">
      <span class="link readonly">切磋</span>. <a class="link" @click="handleLink('闯塔')">闯塔</a>.
      <a class="link" @click="handleLink('战场')">战场</a>. <a class="link" @click="handleLink('擂台')">擂台</a>. <span class="link readonly">坐骑</span>
    </div>
    <div class="section nav">
      <a class="link" @click="router.push('/tree')">古树</a>. <a class="link" @click="handleLink('排行')">排行</a>.
      <span class="link readonly">成就</span>. <a class="link" @click="handleLink('图鉴')">图鉴</a>. <span class="link readonly">攻略</span>
    </div>
    <div class="section nav">
      <a class="link" @click="handleLink('兑换')">兑换</a>. <span class="link readonly">签到</span>.
      <span class="link readonly">论坛</span>. <a class="link" @click="handleLink('VIP')">VIP</a>. <span class="link readonly">安全锁</span>
    </div>

    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>

  </div>
</template>

<style scoped>
.friend-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 10px 12px;
  font-size: 17px;
  line-height: 1.7;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 6px 0;
}

.title {
  font-weight: bold;
}

.tabs {
  margin-top: 4px;
}

.item {
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 6px;
}

.rank {
  display: inline-block;
  min-width: 24px;
}

.rank-name {
  color: #333;
}

.paren {
  color: #333;
}

.name {
  font-weight: bold;
}

.name.red {
  color: #cc0000;
}

.vip {
  color: #cc3300;
  font-weight: bold;
}

.level {
  color: #333;
}

.pager-links .link + .link {
  margin-left: 10px;
}

.pager {
  display: flex;
  align-items: center;
  gap: 6px;
}

.page-input {
  width: 50px;
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

.link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.link.readonly {
  color: #000000;
  cursor: default;
  pointer-events: none;
  text-decoration: none;
}

.link.readonly:hover {
  text-decoration: none;
}

.link.active {
  color: #333;
  font-weight: bold;
  cursor: default;
  text-decoration: none;
}

.gray {
  color: #666666;
}

.small {
  font-size: 17px;
}

.footer {
  margin-top: 16px;
  padding-top: 10px;
  border-top: 1px solid #CCCCCC;
}
</style>
