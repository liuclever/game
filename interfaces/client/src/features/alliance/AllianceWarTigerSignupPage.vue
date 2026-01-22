<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()

const allTargets = ref([])
const loading = ref(true)

// 从后端API获取伏虎军可报名的据点列表
const loadTargets = async () => {
  loading.value = true
  try {
    // 通过查询参数指定军队类型为tiger，确保返回伏虎军的据点列表
    const res = await http.get('/alliance/war/targets', { params: { army: 'tiger' } })
    console.log('伏虎军报名页面 - API响应:', res?.data)
    
    if (res?.data?.ok) {
      const lands = res.data.data?.lands || []
      console.log('伏虎军报名页面 - 获取到的目标列表:', lands)
      
      // 伏虎军只能选择据点（land_type === 'stronghold'）
      const filteredStrongholds = lands.filter(land => land.land_type === 'stronghold')
      console.log('伏虎军报名页面 - 过滤后的据点列表:', filteredStrongholds)
      
      allTargets.value = filteredStrongholds.map((land, index) => ({
        id: land.id,
        seq: index + 1,
        name: land.label,
        signupCount: land.signup_count || 0
      }))
      
      if (allTargets.value.length === 0) {
        console.warn('伏虎军报名页面 - 没有找到可报名的据点')
      }
    } else {
      const error = res?.data?.error || '未知错误'
      console.error('获取据点列表失败', error)
      // 如果API返回错误，显示错误信息
      alert(`获取据点列表失败: ${error}`)
    }
  } catch (err) {
    console.error('获取据点列表失败', err)
    const errorMsg = err?.response?.data?.error || err?.message || '网络错误，请稍后重试'
    alert(`获取据点列表失败: ${errorMsg}`)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadTargets()
})

const visibleTargets = computed(() => allTargets.value)

const handleAttack = (target) => {
  // 跳转到确认页面
  router.push({
    path: '/alliance/war/land-signup-confirm',
    query: {
      land_id: target.id,
      land_name: target.name
    }
  })
}

const goBack = () => {
  router.back()
}

const goWar = () => {
  router.push('/alliance/war')
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="targets-page">
    <div class="section title">【据点详情】</div>
    <div class="section header">序号.据点.报名联盟数</div>

    <div v-if="loading" class="section">加载中...</div>
    <div v-else-if="visibleTargets.length === 0" class="section">
      暂无可报名的据点
    </div>
    <div
      v-else
      v-for="target in visibleTargets"
      :key="target.id"
      class="section row"
    >
      <span>{{ target.seq }}.</span>
      <span class="blue">{{ target.name }}.</span>
      <span>{{ target.signupCount }}</span>
      <a class="link" @click.prevent="handleAttack(target)">攻打</a>
    </div>

    <div class="section footer-links">
      <a class="link" @click.prevent="goBack">返回前页</a>
      <a class="link" @click.prevent="goWar">返回盟战</a>
      <a class="link" @click.prevent="goHome">返回游戏首页</a>
    </div>
  </div>
</template>

<style scoped>
.targets-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 14px 18px 32px;
  font-size: 16px;
  line-height: 1.6;
  font-family: 'SimSun', '宋体', serif;
  color: #000000;
}

.section {
  margin: 6px 0;
}

.title {
  font-weight: bold;
}

.header {
  font-weight: bold;
  margin-top: 2px;
}

.row {
  display: flex;
  align-items: center;
  gap: 4px;
}

.blue {
  color: #0066cc;
}

.link {
  color: #0066cc;
  cursor: pointer;
  margin-left: 8px;
}

.link:hover {
  text-decoration: underline;
}

.footer-links {
  margin-top: 24px;
  display: flex;
  gap: 18px;
}
</style>
