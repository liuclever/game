<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

import { useToast } from '@/composables/useToast'
const { toast } = useToast()
const router = useRouter()

// 动态列表
const dynamics = ref([])
const loading = ref(false)

// 分页
const currentPage = ref(1)
const totalPages = ref(1)
const pageInput = ref('1')
const pageSize = 10

// 加载动态列表
const loadDynamics = async (page = 1) => {
  loading.value = true
  try {
    const res = await http.get('/dynamics/my-dynamics', {
      params: { page, page_size: pageSize }
    })
    if (res.data.ok) {
      dynamics.value = res.data.dynamics || []
      currentPage.value = res.data.page || 1
      totalPages.value = res.data.total_pages || 1
      pageInput.value = String(currentPage.value)
    } else {
      toast.error(res.data.error || '加载失败')
    }
  } catch (e) {
    console.error('加载动态失败', e)
    toast.error('加载失败')
  } finally {
    loading.value = false
  }
}

// 分页跳转
const jumpToPage = () => {
  const page = parseInt(pageInput.value)
  if (page >= 1 && page <= totalPages.value) {
    loadDynamics(page)
  } else {
    toast.error(`请输入1-${totalPages.value}之间的页码`)
    pageInput.value = String(currentPage.value)
  }
}

// 下一页
const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    loadDynamics(currentPage.value + 1)
  }
}

// 末页
const lastPage = () => {
  loadDynamics(totalPages.value)
}

// 查看动态详情
const viewDetail = (dynamic) => {
  if (dynamic.has_detail && dynamic.battle_id) {
    const battleType = dynamic.battle_type || 'arena'
    const battleId = dynamic.battle_id
    
    // 根据对战类型跳转到不同的详情页面
    if (battleType === 'arena') {
      router.push({
        name: 'ArenaBattle',
        query: { id: battleId }
      })
    } else if (battleType === 'zhenyao') {
      router.push({
        path: '/tower/zhenyao/battle',
        query: { id: battleId }
      })
    } else if (battleType === 'battlefield') {
      router.push({
        path: '/battlefield/battle',
        query: { id: battleId }
      })
    } else if (battleType === 'spar') {
      // 切磋战报可以跳转到玩家详情页或专门的战报页
      router.push({
        path: '/player/spar-battle',
        query: { id: battleId }
      })
    } else {
      // 默认跳转到擂台战报
      router.push({
        name: 'ArenaBattle',
        query: { id: battleId }
      })
    }
  }
}

// 返回首页
const goHome = () => {
  router.push('/')
}

onMounted(() => {
  loadDynamics(1)
})
</script>

<template>
  <div class="dynamics-page">
    <div class="section title">【我的动态】</div>
    
    <!-- 动态列表 -->
    <div class="section dynamics-list">
      <div v-if="loading" class="dynamic-item">加载中...</div>
      <div 
        v-for="(dynamic, index) in dynamics" 
        :key="dynamic.id" 
        class="dynamic-item"
      >
        {{ index + 1 + (currentPage - 1) * pageSize }}.({{ dynamic.time }}) {{ dynamic.text }}
        <a 
          v-if="dynamic.has_detail" 
          class="link view-link" 
          @click="viewDetail(dynamic)"
        >
          查看
        </a>
      </div>
      <div v-if="!loading && dynamics.length === 0" class="dynamic-item gray">
        暂无动态
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
.dynamics-page {
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

.title {
  font-weight: bold;
  text-align: center;
  margin: 8px 0;
}

.dynamics-list {
  border: 1px solid #ddd;
  padding: 8px;
  min-height: 300px;
  max-height: 500px;
  overflow-y: auto;
}

.dynamic-item {
  margin: 4px 0;
  padding: 2px 0;
}

.dynamic-item.gray {
  color: #666;
}

.view-link {
  margin-left: 4px;
  color: #0066CC;
}

.pager {
  display: flex;
  gap: 8px;
  align-items: center;
  justify-content: center;
  margin: 8px 0;
}

.page-input {
  width: 50px;
  padding: 2px 4px;
  border: 1px solid #ccc;
  text-align: center;
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

.link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}
</style>
