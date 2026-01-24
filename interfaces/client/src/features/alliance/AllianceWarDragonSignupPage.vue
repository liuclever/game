<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()

const allTargets = ref([])
const loading = ref(true)

// 从后端API获取飞龙军可报名的土地列表
const loadTargets = async () => {
  loading.value = true
  try {
    // 通过查询参数指定军队类型为dragon，确保返回飞龙军的土地列表
    const res = await http.get('/alliance/war/targets', { params: { army: 'dragon' } })
    
    // axios 返回的 res.data 就是后端返回的 JSON 对象 {ok: true, data: {lands: [...]}}
    const responseData = res?.data
    
    console.log('[飞龙军报名] API响应:', responseData)
    
    if (responseData?.ok) {
      // 后端已经根据 army=dragon 过滤了，只返回土地（land_type === 'land'）
      const lands = responseData.data?.lands || []
      
      console.log('[飞龙军报名] 获取到的土地列表:', lands)
      console.log('[飞龙军报名] 土地数量:', lands.length)
      
      // 后端已经过滤了，但为了安全起见，前端再过滤一次，确保只显示土地类型的目标
      const filteredLands = lands.filter(land => {
        const isLand = land.land_type === 'land'
        console.log(`[飞龙军报名] 土地 ${land.id}: land_type=${land.land_type}, isLand=${isLand}`)
        return isLand
      })
      
      console.log('[飞龙军报名] 过滤后的土地列表:', filteredLands)
      console.log('[飞龙军报名] 过滤后数量:', filteredLands.length)
      
      allTargets.value = filteredLands.map((land, index) => ({
        id: land.id,
        seq: index + 1,
        name: land.label || land.name || `土地${land.id}`,
        signupCount: land.signup_count || land.signupCount || 0
      }))
      
      console.log('[飞龙军报名] 最终目标列表:', allTargets.value)
      
      if (allTargets.value.length === 0 && lands.length > 0) {
        console.warn('[飞龙军报名] 警告：后端返回了土地但过滤后为空', {
          lands,
          filteredLands
        })
      }
    } else {
      const error = responseData?.error || '未知错误'
      console.error('[飞龙军报名] 获取土地列表失败', error)
      console.error('[飞龙军报名] 响应数据:', responseData)
      alert(`获取土地列表失败: ${error}`)
    }
  } catch (err) {
    console.error('[飞龙军报名] 获取土地列表异常', err)
    console.error('[飞龙军报名] 错误详情:', {
      message: err?.message,
      response: err?.response,
      status: err?.response?.status,
      data: err?.response?.data
    })
    
    // 如果是401错误（未登录），给出更明确的提示
    if (err?.response?.status === 401) {
      alert('请先登录后再访问')
    } else {
      const errorMsg = err?.response?.data?.error || err?.message || '网络错误，请稍后重试'
      alert(`获取土地列表失败: ${errorMsg}`)
    }
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
    <div class="section title">【土地详情】</div>
    <div class="section header">序号.土地.报名联盟数</div>

    <div v-if="loading" class="section">加载中...</div>
    <div v-else-if="visibleTargets.length === 0" class="section">
      暂无可报名的土地
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
