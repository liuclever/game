<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()

// 加载状态
const loading = ref(true)
const errorMsg = ref('')

// 魔魂信息
const mosoul = ref(null)

// 来源信息（用于返回）
const fromBeastId = ref(null)

// 加载魔魂详情
const loadMoSoulDetail = async () => {
  loading.value = true
  errorMsg.value = ''
  
  const mosoulId = route.params.id
  if (!mosoulId) {
    errorMsg.value = '无效的魔魂ID'
    loading.value = false
    return
  }
  
  try {
    const res = await http.get(`/mosoul/${mosoulId}`)
    if (res.data.ok) {
      mosoul.value = res.data.mosoul
    } else {
      errorMsg.value = res.data.error || '加载失败'
    }
  } catch (err) {
    errorMsg.value = '网络错误，请稍后重试'
    console.error('加载魔魂详情失败:', err)
  } finally {
    loading.value = false
  }
}

// 返回魔魂首页
const goBack = () => {
  if (fromBeastId.value) {
    router.push(`/beast/${fromBeastId.value}/mosoul`)
  } else {
    router.back()
  }
}

// 返回首页
const goHome = () => {
  router.push('/')
}

onMounted(() => {
  // 记录来源幻兽ID
  fromBeastId.value = route.query.beastId || null
  loadMoSoulDetail()
})
</script>

<template>
  <div class="mosoul-detail-page">
    <!-- 加载状态 -->
    <div v-if="loading" class="section">加载中...</div>
    <div v-else-if="errorMsg" class="section error">{{ errorMsg }}</div>
    
    <!-- 魔魂详情 -->
    <template v-else-if="mosoul">
      <div class="section title">【魔魂-{{ mosoul.name }}】</div>
      <div class="section">品阶：{{ mosoul.grade_name }}</div>
      <div class="section">等级：{{ mosoul.level }}</div>
      <div class="section">经验：{{ mosoul.exp }}/{{ mosoul.max_exp }}</div>
      <div class="section">属性：{{ mosoul.effect_text }}</div>
      <div class="section">描述：{{ mosoul.description || `每级增加幻兽${mosoul.effect_text}` }}</div>
      
      <!-- 导航 -->
      <div class="section spacer">
        <a class="link" @click="goBack">返回魔魂首页</a>
      </div>
      <div class="section">
        <a class="link" @click="goHome">返回游戏首页</a>
      </div>
      
    </template>
  </div>
</template>

<style scoped>
.mosoul-detail-page {
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

.title {
  font-weight: bold;
  margin-bottom: 8px;
}

.spacer {
  margin-top: 16px;
}

.error {
  color: red;
}

.link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.gray {
  color: #666666;
}

.small {
  font-size: 17px;
}

.footer {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #CCCCCC;
}
</style>
