<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchHandbookIndex } from '@/services/handbookService'
import { resolveHandbookImage } from './handbookImage'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const errorMsg = ref('')

const categories = ref([])
const categoryId = ref(1)
const pets = ref([])

const currentPage = ref(1)
const totalPages = ref(1)
const pageInput = ref('')

const worldTitle = ref('【图鉴】')

const petThumbSrc = (p) => resolveHandbookImage(p && p.image)

const onImgError = (e) => {
  const img = e?.target
  if (!img) return
  img.src = resolveHandbookImage(null)
}

const pacenameFromRoute = computed(() => {
  const raw = route.query.pacename
  const v = Number(raw || 1)
  return Number.isFinite(v) && v > 0 ? v : 1
})

const pageFromRoute = computed(() => {
  const raw = route.query.page
  const v = Number(raw || 1)
  return Number.isFinite(v) && v > 0 ? v : 1
})

const load = async () => {
  loading.value = true
  errorMsg.value = ''
  try {
    const res = await fetchHandbookIndex({
      pacename: pacenameFromRoute.value,
      page: pageFromRoute.value,
      pageSize: 10,
    })
    if (res.data && res.data.ok) {
      worldTitle.value = res.data.title || worldTitle.value
      categories.value = res.data.categories || []
      categoryId.value = res.data.category_id || pacenameFromRoute.value
      pets.value = res.data.pets || []
      currentPage.value = res.data.page || 1
      totalPages.value = res.data.total_pages || 1
      pageInput.value = String(currentPage.value)
    } else {
      errorMsg.value = (res.data && res.data.error) || '加载失败'
    }
  } catch (e) {
    console.error('加载图鉴失败', e)
    errorMsg.value = '加载失败'
  } finally {
    loading.value = false
  }
}

const selectCategory = (id) => {
  router.push({ path: '/handbook', query: { pacename: id, page: 1 } })
}

const goToPage = (p) => {
  const page = Math.max(1, Math.min(Number(p || 1), totalPages.value || 1))
  router.push({ path: '/handbook', query: { pacename: categoryId.value, page } })
}

const jumpToPage = () => {
  const v = Number(pageInput.value || 1)
  if (!Number.isFinite(v) || v <= 0) return
  goToPage(v)
}

const goDetail = (petId) => {
  if (!petId) return
  router.push({ path: `/handbook/pet/${petId}`, query: { evolution: 0 } })
}

const goHome = () => router.push('/')

watch(
  () => [pacenameFromRoute.value, pageFromRoute.value],
  () => load(),
)

onMounted(() => load())
</script>

<template>
  <div class="handbook-page">
    <div class="section title title-row">
      <span>{{ worldTitle }}</span>
    </div>

    <div class="section" v-if="loading">加载中...</div>
    <div class="section red" v-else-if="errorMsg">{{ errorMsg }}</div>

    <template v-else>
      <div class="section tabs">
        <span v-for="(c, idx) in categories" :key="c.id">
          <a class="link" :class="{ active: Number(c.id) === Number(categoryId) }" @click="selectCategory(c.id)">{{ c.name }}</a>
          <span v-if="idx < categories.length - 1"> | </span>
        </span>
      </div>

      <div class="section list">
        <div v-for="p in pets" :key="p.id" class="item">
          <img class="pet-thumb" :src="petThumbSrc(p)" alt="pet" @error="onImgError" />
          <a class="link pet-name" @click="goDetail(p.id)">{{ p.name }}</a>
        </div>
      </div>

      <div class="section pager-links">
        <a class="link" @click="goToPage(currentPage + 1)" v-if="currentPage < totalPages">下页</a>
        <a class="link" @click="goToPage(totalPages)" v-if="currentPage < totalPages">末页</a>
        <a class="link" @click="goToPage(1)" v-if="currentPage > 1">首页</a>
        <a class="link" @click="goToPage(currentPage - 1)" v-if="currentPage > 1">上页</a>
      </div>

      <div class="section pager">
        {{ currentPage }}/{{ totalPages }}页
        <input class="page-input" v-model="pageInput" />
        <button class="btn" @click="jumpToPage">跳转</button>
      </div>

      <div class="section">
        <a class="link" @click="goHome">返回游戏首页</a>
      </div>
    </template>
  </div>
</template>

<style scoped>
.handbook-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 12px 16px;
  font-size: 16px;
  line-height: 1.8;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 10px 0;
}

.title {
  font-weight: bold;
}

.title-row {
  /* 标题行右侧“简介”入口（不依赖 flex，避免在协作改动中意外失效） */
  position: relative;
}

.intro-link {
  position: absolute;
  right: 0;
  top: 0;
}

.tabs {
  margin-top: 6px;
}

.list {
  margin-top: 10px;
}

.item {
  margin: 6px 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.pet-thumb {
  width: 48px; /* 中等大小（约 1.5x） */
  height: 48px;
  object-fit: contain;
  border: 1px solid #ddd;
  background: #fff;
}

.pet-name {
  font-size: 16px;
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
  color: #CC3300;
  font-weight: bold;
}

.pager-links .link {
  margin-right: 10px;
}

.page-input {
  width: 50px;
  margin: 0 8px;
  font-size: 14px;
}

.btn {
  padding: 4px 10px;
  font-size: 14px;
}

.red {
  color: #CC3300;
}
</style>


