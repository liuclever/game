<script setup>
import { useMessage } from '@/composables/useMessage'
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import http from '@/services/http'

const route = useRoute()
const router = useRouter()

// 背包数据
const { message, messageType, showMessage } = useMessage()

const items = ref([])
const tempItems = ref([])  // 临时背包
const loading = ref(true)
const bagInfo = ref({ capacity: 145, used_slots: 0, temp_slots: 0 })
const transferred = ref([])  // 本次转移的物品

// 分类
const categories = {
  all: '全部',
  material: '材料',
  consumable: '道具',
}
const currentCategory = ref('all')

// 是否显示临时背包
const showTemp = ref(false)

// 名称筛选关键词（卷轴、战骨、召唤球、技能书）
const nameFilter = ref('')

// 关键字搜索（仅正式背包）
const keywordSearch = ref('')

// 分页
const currentPage = ref(1)
const pageSize = 10
const jumpPage = ref(1)

// 加载背包数据（使用新接口）
const loadInventory = async () => {
  try {
    const res = await http.get('/inventory/list')
    if (res.data.ok) {
      items.value = res.data.items
      bagInfo.value = res.data.bag_info
      transferred.value = res.data.transferred || []
      
      // 如果有转移的物品，显示提示
      if (transferred.value.length > 0) {
        const names = transferred.value.map(t => `${t.name}x${t.quantity}`).join('、')
        showMessage(`临时背包物品已自动转入背包：${names}`, 'success')
      }
    }
  } catch (e) {
    console.error('加载背包失败', e)
    // 兼容旧接口
    try {
      const res = await http.get('/inventory')
      items.value = res.data
    } catch (e2) {
      console.error('加载背包失败', e2)
    }
  } finally {
    loading.value = false
  }
}

// 加载临时背包
const loadTempItems = async () => {
  try {
    const res = await http.get('/inventory/temp')
    if (res.data.ok) {
      tempItems.value = res.data.items
    }
  } catch (e) {
    console.error('加载临时背包失败', e)
  }
}

// 切换到临时背包
const switchToTemp = () => {
  showTemp.value = true
  currentCategory.value = 'all'
  nameFilter.value = ''
  keywordSearch.value = ''
  currentPage.value = 1
  loadTempItems()
}

// 切换回正式背包
const switchToNormal = () => {
  showTemp.value = false
  currentPage.value = 1
}

onMounted(() => {
  loadInventory()
  // 支持从“领取/打开礼包”跳回背包时默认显示临时栏：/inventory?tab=temp
  if (String(route.query.tab || '') === 'temp') {
    switchToTemp()
  }
})

// 过滤后的物品
const filteredItems = computed(() => {
  let result = items.value
  
  // 按类型筛选
  if (currentCategory.value !== 'all') {
    result = result.filter(item => item.type === currentCategory.value)
  }
  
  // 按名称关键词筛选
  if (nameFilter.value) {
    result = result.filter(item => item.name.includes(nameFilter.value))
  }

  // 按关键字搜索（仅正式背包）
  if (!showTemp.value && keywordSearch.value) {
    result = result.filter(item => item.name.includes(keywordSearch.value))
  }
  
  return result
})

// 分页后的物品
const pagedItems = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredItems.value.slice(start, start + pageSize)
})

// 总页数
const totalPages = computed(() => {
  return Math.max(1, Math.ceil(filteredItems.value.length / pageSize))
})

// 切换分类
const switchCategory = (cat) => {
  showTemp.value = false
  currentCategory.value = cat
  nameFilter.value = ''  // 清除名称筛选
  keywordSearch.value = ''
  currentPage.value = 1
}

// 按名称筛选
const filterByName = (keyword) => {
  showTemp.value = false
  nameFilter.value = keyword
  currentCategory.value = 'all'  // 重置类型筛选
  keywordSearch.value = ''
  currentPage.value = 1
}

// 翻页
const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}

const firstPage = () => {
  currentPage.value = 1
}

const lastPage = () => {
  currentPage.value = totalPages.value
}

const goToPage = () => {
  const page = parseInt(jumpPage.value)
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

// 使用物品
const useItem = async (item) => {
  const isPrestigeStone = item.item_id === 12001
  if (item.type !== 'consumable' && !isPrestigeStone) {
    showMessage('该物品不可直接使用', 'error')
    return
  }

  const isSummonBall = item.name.includes('召唤球')
  const actionName = isSummonBall ? '开启' : '使用'

  // 已移除确认提示

  try {
    const res = await http.post('/inventory/use', {
      id: item.id,
      quantity: 1
    })

    if (res.data.ok) {
      showMessage(res.data.message || `${actionName}成功！`, 'success')
      loadInventory() // 刷新背包
    } else {
      showMessage(`使用失败: ${res.data.error || '未知错误'}`, 'error')
    }
  } catch (e) {
    console.error('使用物品失败', e)
    showMessage('请求失败，请稍后再试', 'error')
  }
}

const DRAGONPALACE_EXPLORE_GIFT_ITEM_ID = 93001

const openTempGift = (item) => {
  if (!item || item.item_id !== DRAGONPALACE_EXPLORE_GIFT_ITEM_ID) {
    showMessage('该物品暂不支持在此打开', 'info')
    return
  }
  router.push({ path: '/dragonpalace/gift-open', query: { inv_item_id: item.id } })
}

// 返回首页
const goHome = () => {
  router.push('/')
}

// 点击链接
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
    '升级': '/inventory/upgrade',
    '兑换': '/exchange',
    '赞助': '/sponsor',
    '礼包': '/gifts',
    '联盟': '/alliance',
    '盟战': '/alliance/war',
    '化仙': '/huaxian',
    '战场': '/battlefield',
    'VIP': '/vip',
    '提升': '/vip',
    '活力': '/vip',
    '图鉴': '/handbook',
  }
  if (routes[name]) {
    router.push(routes[name])
  } else {
    showMessage(`点击了: ${name}`, 'info')
  }
}
</script>

<template>
  <div class="inventory-page">
    <!-- 消息提示 -->
    <div v-if="message" class="message" :class="messageType">
      {{ message }}
    </div>

    <!-- 背包标题 -->
    <div class="section title">
      【{{ bagInfo.bag_name || '背包' }}({{ bagInfo.used_slots }}/{{ bagInfo.capacity }})】 <a class="link" @click="handleLink('升级')">升级</a>
    </div>

    <!-- 分类标签 -->
    <div class="section">
      <a 
        class="link" 
        :class="{ active: !showTemp && currentCategory === 'consumable' && !nameFilter }"
        @click="switchCategory('consumable')"
      >道具</a> | 
      <a 
        class="link"
        :class="{ active: !showTemp && currentCategory === 'material' && !nameFilter }"
        @click="switchCategory('material')"
      >材料</a> | 
      <a 
        class="link"
        :class="{ active: !showTemp && nameFilter === '召唤球' }"
        @click="filterByName('召唤球')"
      >召唤球</a>
    </div>
    <div class="section">
      <a 
        class="link"
        :class="{ active: !showTemp && nameFilter === '战骨' }"
        @click="filterByName('战骨')"
      >战骨</a> | 
      <a 
        class="link"
        :class="{ active: !showTemp && nameFilter === '卷轴' }"
        @click="filterByName('卷轴')"
      >卷轴</a> | 
      <a 
        class="link"
        :class="{ active: !showTemp && nameFilter === '技能书' }"
        @click="filterByName('技能书')"
      >技能书</a>
    </div>
    <div class="section">
      <a 
        class="link"
        :class="{ active: showTemp }"
        @click="switchToTemp"
      >临时</a>
    </div>

    <div class="section" v-if="!showTemp">
      关键字搜索:
      <input
        type="text"
        v-model="keywordSearch"
        class="page-input"
        style="width: 120px"
        placeholder="输入物品名"
      />
      <a class="link" @click="keywordSearch = ''; currentPage = 1">清空</a>
    </div>

    <!-- 正式背包物品列表 -->
    <div class="items-list" v-if="!loading && !showTemp">
      <div v-if="pagedItems.length === 0" class="section gray">
        背包空空如也...
      </div>
      <div v-for="item in pagedItems" :key="item.id" class="section">
        <a class="link" @click="useItem(item)">{{ item.name }}</a>×{{ item.quantity }}
      </div>
    </div>

    <!-- 临时背包物品列表 -->
    <div class="items-list" v-if="!loading && showTemp">
      <div class="section gray small">临时背包物品将在每日24点清空，请及时整理背包取出</div>
      <div v-if="tempItems.length === 0" class="section gray">
        临时背包为空
      </div>
      <div v-for="item in tempItems" :key="item.id" class="section">
        <a class="link">{{ item.name }}</a>×{{ item.quantity }}
        <a
          v-if="item.item_id === DRAGONPALACE_EXPLORE_GIFT_ITEM_ID"
          class="link"
          @click="openTempGift(item)"
        >打开</a>
        <span class="gray small"> ({{ item.created_at }})</span>
      </div>
    </div>

    <div v-if="loading" class="section gray">加载中...</div>

    <!-- 分页（仅正式背包显示） -->
    <div class="section" v-if="!showTemp && filteredItems.length > 0">
      <a class="link" @click="nextPage">下页</a> 
      <a class="link" @click="prevPage">上页</a> 
      <a class="link" @click="firstPage">首页</a> 
      <a class="link" @click="lastPage">末页</a>
    </div>
    <div class="section" v-if="!showTemp && filteredItems.length > 0">
      {{ currentPage }}/{{ totalPages }}页 
      <input 
        type="text" 
        v-model="jumpPage" 
        class="page-input"
      />
      <button class="page-btn" @click="goToPage">跳转</button>
    </div>

    <!-- 功能链接 -->
    <div class="section">
      <a class="link" @click="handleLink('整理背包')">整理背包</a>
    </div>
    <div class="section">
      寄存道具到 <a class="link" @click="handleLink('联盟寄存仓库')">联盟寄存仓库</a>
    </div>

    <!-- 皇城 -->
    <div class="section spacer">
      皇城:<span class="link readonly">召唤之王挑战赛</span>
    </div>

    <!-- 导航菜单 -->
    <div class="section">
      <a class="link" @click="handleLink('幻兽')">幻兽</a>. 
      <a class="link active">背包</a>. 
      <a class="link" @click="handleLink('商城')">商城</a>. 
      <a class="link" @click="handleLink('赞助')">赞助</a>. 
      <a class="link" @click="handleLink('礼包')">礼包</a>
    </div>
    <div class="section">
      <a class="link" @click="handleLink('联盟')">联盟</a>. 
      <a class="link" @click="handleLink('盟战')">盟战</a>. 
      <a class="link" @click="handleLink('地图')">地图</a>. 
      <span class="link readonly">天赋</span>. 
      <a class="link" @click="handleLink('化仙')">化仙</a>
    </div>
    <div class="section">
      <span class="link readonly">切磋</span>. 
      <a class="link" @click="handleLink('闯塔')">闯塔</a>. 
      <a class="link" @click="handleLink('战场')">战场</a>. 
      <a class="link" @click="handleLink('擂台')">擂台</a>. 
      <span class="link readonly">坐骑</span>
    </div>
    <div class="section">
      <a class="link" @click="router.push('/tree')">古树</a>. 
      <a class="link" @click="handleLink('排行')">排行</a>. 
      <span class="link readonly">成就</span>. 
      <a class="link" @click="handleLink('图鉴')">图鉴</a>. 
      <span class="link readonly">攻略</span>
    </div>
    <div class="section">
      <a class="link" @click="handleLink('兑换')">兑换</a>. 
      <span class="link readonly">签到</span>. 
      <span class="link readonly">论坛</span>. 
      <a class="link" @click="handleLink('VIP')">VIP</a>. 
      <span class="link readonly">安全锁</span>
    </div>

    <!-- 返回首页 -->
    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>

  </div>
</template>

<style scoped>
.inventory-page {
  background: #FFF8DC;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 13px;
  line-height: 1.6;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 2px 0;
}

.title {
  margin-bottom: 8px;
}

.spacer {
  margin-top: 16px;
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
  color: #CC3300;
  font-weight: bold;
}

.gray {
  color: #666666;
}

.small {
  font-size: 11px;
}

.items-list {
  margin: 8px 0;
  padding-left: 8px;
}

.page-input {
  width: 40px;
  font-size: 12px;
  border: 1px solid #CCCCCC;
  padding: 1px 4px;
}

.page-btn {
  font-size: 12px;
  padding: 1px 8px;
  background: #F0F0F0;
  border: 1px solid #CCCCCC;
  cursor: pointer;
}

.page-btn:hover {
  background: #E0E0E0;
}

.footer {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #CCCCCC;
}

/* 消息提示样式 */
.message {
  padding: 12px;
  margin: 12px 0;
  border-radius: 4px;
  font-weight: bold;
  text-align: center;
}

.message.success {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.message.error {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.message.info {
  background: #d1ecf1;
  color: #0c5460;
  border: 1px solid #bee5eb;
}

</style>
