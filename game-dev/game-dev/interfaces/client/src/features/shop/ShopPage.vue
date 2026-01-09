<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()

// 数据
const categories = ref([])
const currentCategory = ref('copper')
const items = ref([])
const gold = ref(0)
const yuanbao = ref(0)
const currency = ref('gold')
const loading = ref(false)

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
      items.value = res.data.items
      gold.value = res.data.gold
      yuanbao.value = res.data.yuanbao
      currency.value = res.data.currency
    }
  } catch (e) {
    console.error('加载商品失败', e)
  } finally {
    loading.value = false
  }
}

// 分页计算
const pagedItems = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return items.value.slice(start, start + pageSize)
})

const totalPages = computed(() => {
  return Math.max(1, Math.ceil(items.value.length / pageSize))
})

// 切换分类
const switchCategory = (key) => {
  currentCategory.value = key
  currentPage.value = 1
  loadItems()
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

    <!-- 商品列表 -->
    <div class="item-list" v-if="!loading">
      <div v-for="item in pagedItems" :key="item.id" class="item-row">
        <a class="link item-name" @click="goItemDetail(item)">{{ item.name }}</a>
        <span class="item-price">.{{ item.price }}{{ currency === 'gold' ? '铜钱' : '元宝' }}.</span>
        <a class="link buy-btn" @click="buyItem(item)">购买</a>
      </div>
      <div v-if="items.length === 0" class="empty">
        暂无商品
      </div>
    </div>
    <div v-else class="loading">加载中...</div>

    <!-- 分页 -->
    <div class="pagination" v-if="items.length > 0">
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
  background: #FFF8DC;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 13px;
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
  font-size: 11px;
}
</style>
