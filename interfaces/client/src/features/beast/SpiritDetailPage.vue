<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()

// ========== 数据状态 ==========
const loading = ref(true)
const errorMsg = ref('')
const spirit = ref(null)

// 属性名称映射
const attrNames = {
  hp_pct: '气血',
  attack_pct: '攻击',
  physical_attack_pct: '物理攻击',
  magic_attack_pct: '法术攻击',
  physical_defense_pct: '物理防御',
  magic_defense_pct: '法术防御',
  speed_pct: '速度',
}

// 元素名称映射
const elementNames = {
  earth: '土',
  fire: '火',
  water: '水',
  wood: '木',
  metal: '金',
  god: '神',
}

// 各元素品质区间配置 (basis points: 1bp = 0.01%)
const qualityTiers = {
  earth: [
    { name: '普通', min: 500, max: 1000 },
    { name: '精良', min: 1000, max: 1900 },
    { name: '优秀', min: 1900, max: 2300 },
    { name: '传奇', min: 2300, max: 2500 },
  ],
  fire: [
    { name: '普通', min: 1000, max: 1400 },
    { name: '精良', min: 1400, max: 2300 },
    { name: '优秀', min: 2300, max: 2800 },
    { name: '传奇', min: 2800, max: 3000 },
  ],
  water: [
    { name: '普通', min: 1500, max: 1800 },
    { name: '精良', min: 1800, max: 2900 },
    { name: '优秀', min: 2900, max: 3300 },
    { name: '传奇', min: 3300, max: 3500 },
  ],
  wood: [
    { name: '普通', min: 2500, max: 3000 },
    { name: '精良', min: 3000, max: 3900 },
    { name: '优秀', min: 3900, max: 4300 },
    { name: '传奇', min: 4300, max: 4500 },
  ],
  metal: [
    { name: '普通', min: 3500, max: 4000 },
    { name: '精良', min: 4000, max: 5100 },
    { name: '优秀', min: 5100, max: 5700 },
    { name: '传奇', min: 5700, max: 6000 },
  ],
  god: [
    { name: '普通', min: 4500, max: 5000 },
    { name: '精良', min: 5000, max: 6000 },
    { name: '优秀', min: 6000, max: 6600 },
    { name: '传奇', min: 6600, max: 7000 },
  ],
}

// ========== 加载数据 ==========
const loadData = async () => {
  loading.value = true
  errorMsg.value = ''
  
  const spiritId = route.params.id
  if (!spiritId) {
    errorMsg.value = '缺少战灵ID'
    loading.value = false
    return
  }
  
  try {
    const res = await http.get(`/spirit/${spiritId}`)
    if (res.data.ok) {
      spirit.value = res.data.spirit
    } else {
      errorMsg.value = res.data.error || '获取战灵信息失败'
    }
  } catch (err) {
    errorMsg.value = '网络错误，请稍后重试'
    console.error('获取战灵信息失败:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})

// ========== 计算属性 ==========
const spiritName = computed(() => {
  if (!spirit.value) return ''
  const elementName = elementNames[spirit.value.element] || spirit.value.element
  return `${spirit.value.race}·${elementName}灵`
})

// 判断战灵是否被锁定
const isLocked = computed(() => {
  if (!spirit.value || !spirit.value.lines) return false
  return spirit.value.lines.some(ln => ln.locked)
})

// 获取属性显示名称
const getAttrName = (attrKey) => {
  return attrNames[attrKey] || attrKey
}

// 格式化百分比值
const formatPercent = (valueBp) => {
  return (valueBp / 100).toFixed(2) + '%'
}

// 获取品质名称
const getQualityName = (element, valueBp) => {
  const tiers = qualityTiers[element]
  if (!tiers) return ''
  for (const tier of tiers) {
    if (valueBp >= tier.min && valueBp < tier.max) {
      return tier.name
    }
  }
  // 如果值等于最大值，返回最高品质
  if (tiers.length > 0 && valueBp >= tiers[tiers.length - 1].min) {
    return tiers[tiers.length - 1].name
  }
  return '普通'
}

// ========== 操作 ==========
const toggleLock = async () => {
  if (!spirit.value) return
  
  try {
    const newLockState = !isLocked.value
    const res = await http.post(`/spirit/${spirit.value.id}/lock-line`, {
      line_index: 1,
      locked: newLockState
    })
    
    if (res.data.ok) {
      spirit.value.lines = res.data.spirit.lines
    } else {
      alert(res.data.error || '操作失败')
    }
  } catch (err) {
    alert('网络错误，请稍后重试')
    console.error('锁定/解锁战灵失败:', err)
  }
}

const sellSpirit = async () => {
  if (!spirit.value) return
  
  if (isLocked.value) {
    alert('该战灵已锁定，无法出售')
    return
  }
  
  if (!confirm(`确定要出售 ${spiritName.value} 吗？`)) {
    return
  }
  
  try {
    const res = await http.post(`/spirit/${spirit.value.id}/sell`)
    if (res.data.ok) {
      alert(`出售成功，获得 ${res.data.gained_spirit_power || 0} 灵力`)
      router.push('/spirit/warehouse')
    } else {
      alert(res.data.error || '出售失败')
    }
  } catch (err) {
    alert('网络错误，请稍后重试')
    console.error('出售战灵失败:', err)
  }
}

// ========== 导航 ==========
const goBack = () => {
  router.back()
}

const goHome = () => {
  router.push('/')
}

// 跳转到洗练页面
const goToRefine = () => {
  if (!spirit.value) return
  router.push(`/spirit/${spirit.value.id}/refine`)
}

// 激活属性条
const unlockLine = async (lineIndex) => {
  if (!spirit.value) return
  
  try {
    const res = await http.post(`/spirit/${spirit.value.id}/unlock-line`, {
      line_index: lineIndex
    })
    if (res.data.ok) {
      spirit.value.lines = res.data.spirit.lines
      alert('激活成功')
    } else {
      // 检查是否钥匙不足
      const errorMsg = res.data.error || '激活失败'
      if (errorMsg.includes('物品') || errorMsg.includes('不足') || errorMsg.includes('钥匙')) {
        router.push('/spirit/key-insufficient')
      } else {
        alert(errorMsg)
      }
    }
  } catch (err) {
    // 400错误通常是钥匙不足，直接跳转到提示页面
    if (err.response && err.response.status === 400) {
      router.push('/spirit/key-insufficient')
    } else {
      alert('网络错误，请稍后重试')
    }
    console.error('激活属性条失败:', err)
  }
}

// 获取激活所需钥匙数量（严格按《战灵拓展》：随元素与条数变化）
const UNLOCK_KEY_COST = {
  earth: { 2: 1, 3: 2 },
  fire: { 2: 2, 3: 3 },
  water: { 2: 3, 3: 4 },
  wood: { 2: 4, 3: 5 },
  metal: { 2: 5, 3: 6 },
  god: { 2: 6, 3: 7 },
}
const getUnlockKeyCost = (lineIndex) => {
  const element = spirit.value?.element || 'earth'
  const mp = UNLOCK_KEY_COST[element] || UNLOCK_KEY_COST.earth
  return mp[lineIndex] || 0
}

// 返回战灵首页
const goToSpiritPage = () => {
  router.back()
}
</script>

<template>
  <div class="spirit-detail-page">
    <!-- 加载状态 -->
    <div v-if="loading" class="section">加载中...</div>
    <div v-else-if="errorMsg" class="section error">{{ errorMsg }}</div>
    
    <template v-else-if="spirit">
      <!-- 标题 -->
      <div class="section title-section">
        <span class="title">【战灵-属性】</span>
        <a class="link" @click="goToRefine">洗练</a>
      </div>
      
      <!-- 当前战灵信息 -->
      <div class="section">
        当前：{{ elementNames[spirit.element] }}灵·{{ spirit.race }}
      </div>
      
      <!-- 属性条列表（固定3条） -->
      <template v-for="index in 3" :key="index">
        <div class="section attr-line">
          <template v-if="spirit.lines && spirit.lines[index - 1] && spirit.lines[index - 1].unlocked">
            {{ index }}.{{ getAttrName(spirit.lines[index - 1].attr || spirit.lines[index - 1].attr_key) }}+{{ formatPercent(spirit.lines[index - 1].value_bp) }}({{ getQualityName(spirit.element, spirit.lines[index - 1].value_bp) }})
          </template>
          <template v-else>
            {{ index }}.未激活.<a class="link" @click="unlockLine(index)">激活</a>（钥匙×{{ getUnlockKeyCost(index) }}）
          </template>
        </div>
      </template>
      
      <!-- 导航 -->
      <div class="section spacer">
        <a class="link" @click="goToSpiritPage">返回战灵首页</a>
      </div>
      <div class="section">
        <a class="link" @click="goHome">返回游戏首页</a>
      </div>
    </template>
  </div>
</template>

<style scoped>
.spirit-detail-page {
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
  margin-bottom: 4px;
}

.title-section .title {
  font-weight: bold;
  margin-right: 8px;
}

.attr-line {
  color: #333;
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

.error {
  color: red;
}

.footer {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #ccc;
}

.gray {
  color: #666;
}

.small {
  font-size: 17px;
}
</style>
