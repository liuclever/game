<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()

// 数据
const categories = ref([])
const currentCategory = ref('copper')
const items = ref([])
const allItems = ref([])  // 所有商品（用于前端筛选）
const gold = ref(0)
const yuanbao = ref(0)
const currency = ref('gold')
const loading = ref(false)

// 物品类型分类筛选
const itemTypeFilter = ref('')  // 'consumable', 'material', 或名称关键词
const keywordSearch = ref('')  // 关键字搜索

// 分页
const currentPage = ref(1)
const pageSize = 8
const jumpPage = ref(1)

// 加载分类
const loadCategories = async () => {
  try {
    const res = await http.get('/shop/categories')
    if (res.data.ok) {
      categories.value = res.data.categories
    }
  } catch (e) {
    console.error('加载分类失败', e)
  }
}

// 加载商品
const loadItems = async () => {
  loading.value = true
  try {
    const res = await http.get('/shop/items', {
      params: { category: currentCategory.value }
    })
    if (res.data.ok) {
      allItems.value = res.data.items || []
      items.value = res.data.items || []
      gold.value = res.data.gold || 0
      yuanbao.value = res.data.yuanbao || 0
      currency.value = res.data.currency || 'gold'
      // 切换分类时重置筛选
      itemTypeFilter.value = ''
      keywordSearch.value = ''
      currentPage.value = 1
    }
  } catch (e) {
    console.error('加载商品失败', e)
    allItems.value = []
    items.value = []
  } finally {
    loading.value = false
  }
}

// 筛选后的商品
const filteredItems = computed(() => {
  // 如果没有商品数据，返回空数组
  if (!allItems.value || allItems.value.length === 0) {
    return []
  }
  
  let result = allItems.value
  
  // 按物品类型筛选
  if (itemTypeFilter.value) {
    if (itemTypeFilter.value === 'consumable') {
      // 道具类型筛选（根据商品名称判断）
      result = result.filter(item => {
        const name = item.name || ''
        // 道具：药、丹、草、符、香、卡等消耗品
        return name.includes('药') || name.includes('丹') || name.includes('草') || 
               name.includes('符') || name.includes('香') || name.includes('卡') ||
               name.includes('喇叭') || name.includes('宝箱')
      })
    } else if (itemTypeFilter.value === 'material') {
      // 材料类型筛选
      result = result.filter(item => {
        const name = item.name || ''
        // 材料：结晶、石、晶、魂、碎片等
        return name.includes('材料') || name.includes('石') || name.includes('晶') ||
               name.includes('魂') || name.includes('碎片') || name.includes('进化')
      })
    } else if (itemTypeFilter.value === '召唤球') {
      // 召唤球筛选：捕捉球、强力捕捉球等
      result = result.filter(item => {
        const name = item.name || ''
        // 匹配捕捉球、强力捕捉球等，排除宝箱
        return (name.includes('捕捉球') || name.includes('球')) && !name.includes('宝箱')
      })
    } else if (itemTypeFilter.value === '战骨') {
      // 战骨筛选：包含"骨"的商品
      result = result.filter(item => {
        const name = item.name || ''
        return name.includes('骨')
      })
    } else if (itemTypeFilter.value === '卷轴') {
      // 卷轴筛选：包含"卷轴"的商品
      result = result.filter(item => {
        const name = item.name || ''
        return name.includes('卷轴')
      })
    } else if (itemTypeFilter.value === '技能书') {
      // 技能书筛选：包含"书"的商品
      result = result.filter(item => {
        const name = item.name || ''
        return name.includes('书') || name.includes('技能')
      })
    }
  }
  
  // 按关键字搜索
  if (keywordSearch.value) {
    result = result.filter(item => {
      const name = item.name || ''
      return name.includes(keywordSearch.value)
    })
  }
  
  return result
})

// 分页计算
const pagedItems = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredItems.value.slice(start, start + pageSize)
})

const totalPages = computed(() => {
  return Math.max(1, Math.ceil(filteredItems.value.length / pageSize))
})

// 切换分类
const switchCategory = (key) => {
  currentCategory.value = key
  currentPage.value = 1
  itemTypeFilter.value = ''
  keywordSearch.value = ''
  loadItems()
}

// 切换物品类型筛选
const switchItemTypeFilter = (filter) => {
  itemTypeFilter.value = filter
  keywordSearch.value = ''
  currentPage.value = 1
}

// 清空搜索
const clearSearch = () => {
  keywordSearch.value = ''
  currentPage.value = 1
}

// 分页操作
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

// 购买商品 - 跳转到详情页
const buyItem = (item) => {
  router.push('/shop/item/' + item.id + '?category=' + currentCategory.value)
}

// 查看商品详情
const goItemDetail = (item) => {
  router.push('/shop/item/' + item.id + '?category=' + currentCategory.value)
}

// 返回首页
const goHome = () => {
  router.push('/')
}

onMounted(() => {
  // 读取URL中的分类参数
  if (route.query.category) {
    currentCategory.value = route.query.category
  }
  loadCategories()
  loadItems()
})
</script>

<template>
  <div class="shop-page">
    <!-- 分类Tab -->
    <div class="tabs">
      <template v-for="(cat, idx) in categories" :key="cat.key">
        <a 
          class="tab-link" 
          :class="{ active: currentCategory === cat.key }"
          @click="switchCategory(cat.key)"
        >{{ cat.name }}</a>
        <span v-if="idx < categories.length - 1" class="divider">|</span>
      </template>
    </div>

    <!-- 货币显示 -->
    <div class="currency-info">
      <div>铜钱:{{ gold }}</div>
      <div>元宝:{{ yuanbao }}</div>
    </div>

    <!-- 物品类型分类筛选 -->
    <div class="section">
      <a 
        class="link" 
        :class="{ active: itemTypeFilter === 'consumable' }"
        @click="switchItemTypeFilter('consumable')"
      >道具</a> | 
      <a 
        class="link"
        :class="{ active: itemTypeFilter === 'material' }"
        @click="switchItemTypeFilter('material')"
      >材料</a> | 
      <a 
        class="link"
        :class="{ active: itemTypeFilter === '召唤球' }"
        @click="switchItemTypeFilter('召唤球')"
      >召唤球</a>
    </div>
    <div class="section">
      <a 
        class="link"
        :class="{ active: itemTypeFilter === '战骨' }"
        @click="switchItemTypeFilter('战骨')"
      >战骨</a> | 
      <a 
        class="link"
        :class="{ active: itemTypeFilter === '卷轴' }"
        @click="switchItemTypeFilter('卷轴')"
      >卷轴</a> | 
      <a 
        class="link"
        :class="{ active: itemTypeFilter === '技能书' }"
        @click="switchItemTypeFilter('技能书')"
      >技能书</a>
    </div>

    <!-- 关键字搜索 -->
    <div class="section">
      关键字搜索:
      <input
        type="text"
        v-model="keywordSearch"
        class="page-input"
        style="width: 120px"
        placeholder="输入物品名"
      />
      <a class="link" @click="clearSearch">清空</a>
    </div>

    <!-- 商品列表 -->
    <div class="item-list" v-if="!loading">
      <div v-for="item in pagedItems" :key="item.id" class="item-row">
        <a class="link item-name" @click="goItemDetail(item)">{{ item.name }}</a>
        <span class="item-price">.{{ item.price }}{{ currency === 'gold' ? '铜钱' : '元宝' }}.</span>
        <a class="link buy-btn" @click="buyItem(item)">购买</a>
      </div>
      <div v-if="filteredItems.length === 0 && allItems.length > 0" class="empty">
        暂无符合条件的商品
      </div>
      <div v-else-if="allItems.length === 0" class="empty">
        暂无商品
      </div>
    </div>
    <div v-else class="loading">加载中...</div>

    <!-- 分页 -->
    <div class="pagination" v-if="filteredItems.length > 0">
      <a class="link" @click="nextPage">下页</a> 
      <a class="link" @click="prevPage">上页</a> 
      <a class="link" @click="firstPage">首页</a> 
      <a class="link" @click="lastPage">末页</a>
      <div class="page-info">
        {{ currentPage }}/{{ totalPages }}页
        <input type="text" v-model="jumpPage" class="page-input" />
        <button class="page-btn" @click="goToPage">跳转</button>
      </div>
    </div>

    <!-- 返回 -->
    <div class="footer-section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>

  </div>
</template>

<style scoped>
.shop-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 12px 16px;
  font-size: 16px;
  line-height: 1.8;
  font-family: SimSun, "宋体", serif;
}

.tabs {
  margin-bottom: 8px;
}

.tab-link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: none;
}

.tab-link:hover {
  text-decoration: underline;
}

.tab-link.active {
  color: #000;
  font-weight: bold;
}

.divider {
  margin: 0 4px;
  color: #999;
}

.currency-info {
  margin-bottom: 8px;
}

.section {
  margin: 4px 0;
}

.link.active {
  color: #000;
  font-weight: bold;
}

.item-list {
  margin-bottom: 16px;
}

.item-row {
  margin: 2px 0;
}

.item-name {
  color: #CC3300;
}

.item-price {
  color: #000;
}

.buy-btn {
  color: #0066CC;
}

.link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.empty {
  color: #999;
  padding: 20px 0;
}

.loading {
  color: #999;
  padding: 20px 0;
}

.pagination {
  margin: 8px 0;
}

.page-info {
  margin-top: 4px;
}

.page-input {
  width: 40px;
  font-size: 18px;
  border: 1px solid #CCCCCC;
  padding: 1px 4px;
}

.page-btn {
  font-size: 18px;
  padding: 1px 8px;
  background: #ffffff;
  border: 1px solid #CCCCCC;
  cursor: pointer;
}

.page-btn:hover {
  background: #ffffff;
}

.footer-section {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #CCCCCC;
}

.footer {
  margin-top: 10px;
}

.gray {
  color: #666666;
}

.small {
  font-size: 17px;
}
</style>
