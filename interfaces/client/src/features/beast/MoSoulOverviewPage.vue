<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()

// 加载状态
const loading = ref(true)
const errorMsg = ref('')

// 储魂器数据
const warehouseCount = ref(0)
const warehouseCapacity = ref(90)

// 幻兽魔魂列表
const beasts = ref([])

// 加载数据
const loadData = async () => {
  loading.value = true
  errorMsg.value = ''
  
  try {
    const res = await http.get('/mosoul/overview')
    if (res.data.ok) {
      warehouseCount.value = res.data.warehouse_count || 0
      warehouseCapacity.value = res.data.warehouse_capacity || 90
      beasts.value = res.data.beasts || []
    } else {
      errorMsg.value = res.data.error || '加载失败'
    }
  } catch (err) {
    errorMsg.value = '网络错误，请稍后重试'
    console.error('加载魔魂总览失败:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})

// 查看储魂器
const viewWarehouse = () => {
  router.push('/mosoul/warehouse')
}

// 猎魂
const goHunting = () => {
  router.push('/mosoul/hunting')
}

// 查看幻兽魔魂详情
const viewBeastMoSoul = (beastId) => {
  router.push(`/beast/${beastId}/mosoul`)
}

// 返回首页
const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="mosoul-overview-page">
    <!-- 标题 -->
    <div class="section title-section">
      【魔魂】 <a class="link" @click="() => window.alert('魔魂简介：魔魂可以大幅提升幻兽的属性，30级后可装备魔魂。')">简介</a>
    </div>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="section">加载中...</div>
    <div v-else-if="errorMsg" class="section error">{{ errorMsg }}</div>
    
    <template v-else>
      <!-- 储魂器 -->
      <div class="section">
        储魂器:{{ warehouseCount }}/{{ warehouseCapacity }}.<a class="link" @click="viewWarehouse">查看</a>| <a class="link" @click="goHunting">猎魂</a>
      </div>
      
      <!-- 幻兽魔魂标题 -->
      <div class="section">
        幻兽魔魂：
      </div>
      
      <!-- 幻兽列表 -->
      <div v-for="beast in beasts" :key="beast.id" class="section">
        <template v-if="beast.status === '战'">
          <span class="status-war">战</span>.
        </template>
        <template v-else>
          <span class="status-wait">待</span>.
        </template>
        <a class="link beast-name" @click="viewBeastMoSoul(beast.id)">{{ beast.name }}-{{ beast.realm }}</a>({{ beast.level }}级).
        <template v-if="beast.max_slots > 0">
          {{ beast.used_slots }}/{{ beast.max_slots }}
        </template>
        <template v-else>
          {{ beast.status_text }}
        </template>
      </div>
      
      <!-- 导航 -->
      <div class="section spacer">
        <a class="link" @click="goHome">返回游戏首页</a>
      </div>
    </template>
  </div>
</template>

<style scoped>
.mosoul-overview-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 16px;
  line-height: 1.6;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 2px 0;
}

.title-section {
  font-weight: bold;
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

.beast-name {
  color: #0066CC;
}

.status-war {
  color: #CC6600;
  font-weight: bold;
}

.status-wait {
  color: #666;
}

.error {
  color: red;
}

.footer {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #CCCCCC;
}

.gray {
  color: #666666;
}

.small {
  font-size: 17px;
}
</style>
