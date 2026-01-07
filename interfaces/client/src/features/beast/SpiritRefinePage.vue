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
const account = ref(null)

// 属性名称映射
const attrNames = {
  hp_pct: '气血',
  attack_pct: '攻击',
  physical_attack_pct: '物攻',
  magic_attack_pct: '法攻',
  physical_defense_pct: '物防',
  magic_defense_pct: '法防',
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

// 洗练消耗配置（根据元素和锁定词条数）
const refineCostByElementAndLocked = {
  earth: { 0: 1, 1: 3, 2: 9 },
  fire: { 0: 3, 1: 9, 2: 27 },
  water: { 0: 6, 1: 18, 2: 54 },
  wood: { 0: 9, 1: 27, 2: 81 },
  metal: { 0: 15, 1: 45, 2: 135 },
  god: { 0: 30, 1: 90, 2: 270 },
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
    // 并行加载战灵信息和账户信息
    const [spiritRes, accountRes] = await Promise.all([
      http.get(`/spirit/${spiritId}`),
      http.get('/spirit/account')
    ])
    
    if (spiritRes.data.ok) {
      spirit.value = spiritRes.data.spirit
    } else {
      errorMsg.value = spiritRes.data.error || '获取战灵信息失败'
    }
    
    if (accountRes.data.ok) {
      account.value = accountRes.data.account
    }
  } catch (err) {
    errorMsg.value = '网络错误，请稍后重试'
    console.error('加载数据失败:', err)
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
  return `${elementName}灵·${spirit.value.race}`
})

// 计算锁定的词条数量
const lockedCount = computed(() => {
  if (!spirit.value || !spirit.value.lines) return 0
  return spirit.value.lines.filter(ln => ln.unlocked && ln.locked).length
})

// 计算洗练消耗（根据元素和锁定词条数）
const refineCost = computed(() => {
  if (!spirit.value) return 1
  const element = spirit.value.element || 'earth'
  const elementCosts = refineCostByElementAndLocked[element] || refineCostByElementAndLocked.earth
  return elementCosts[lockedCount.value] || elementCosts[0] || 1
})

// 当前灵力
const currentSpiritPower = computed(() => {
  return account.value?.spirit_power || 0
})

// 判断战灵是否被锁定（第一条词条）
const isFirstLineLocked = computed(() => {
  if (!spirit.value || !spirit.value.lines || !spirit.value.lines[0]) return false
  return spirit.value.lines[0].locked
})

// 获取属性显示名称
const getAttrName = (attrKey) => {
  return attrNames[attrKey] || attrKey
}

// 格式化百分比值
const formatPercent = (valueBp) => {
  return '+' + (valueBp / 100).toFixed(0)
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
  if (tiers.length > 0 && valueBp >= tiers[tiers.length - 1].min) {
    return tiers[tiers.length - 1].name
  }
  return '普通'
}

// 获取激活所需钥匙数量
const getUnlockKeyCost = (lineIndex) => {
  return lineIndex === 2 ? 1 : 2
}

// ========== 操作 ==========
// 锁定/解锁第一条词条
const toggleFirstLineLock = async () => {
  if (!spirit.value) return
  
  try {
    const newLockState = !isFirstLineLocked.value
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
    console.error('锁定/解锁词条失败:', err)
  }
}

// 确定洗练
const confirmRefine = async () => {
  if (!spirit.value) return
  
  try {
    const res = await http.post(`/spirit/${spirit.value.id}/refine`)
    if (res.data.ok) {
      spirit.value.lines = res.data.spirit.lines
      // 更新账户灵力
      if (res.data.account) {
        account.value = res.data.account
      }
      // 不弹窗，直接更新页面显示
    } else {
      alert(res.data.error || '洗练失败')
    }
  } catch (err) {
    alert('网络错误，请稍后重试')
    console.error('洗练战灵失败:', err)
  }
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

// ========== 导航 ==========
const goToSpiritPage = () => {
  router.back()
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="spirit-refine-page">
    <!-- 加载状态 -->
    <div v-if="loading" class="section">加载中...</div>
    <div v-else-if="errorMsg" class="section error">{{ errorMsg }}</div>
    
    <template v-else-if="spirit">
      <!-- 标题 -->
      <div class="section title-section">
        <span class="title">【战灵-属性】</span>
        <a class="link" @click="confirmRefine">确定洗练</a>
      </div>
      
      <!-- 当前战灵信息 -->
      <div class="section">
        当前：{{ spiritName }}
      </div>
      
      <!-- 属性条列表（固定3条） -->
      <template v-for="index in 3" :key="index">
        <div class="section attr-line">
          <template v-if="spirit.lines && spirit.lines[index - 1] && spirit.lines[index - 1].unlocked">
            {{ index }}.{{ getAttrName(spirit.lines[index - 1].attr || spirit.lines[index - 1].attr_key) }}{{ formatPercent(spirit.lines[index - 1].value_bp) }}({{ getQualityName(spirit.element, spirit.lines[index - 1].value_bp) }})
            <template v-if="index === 1">
              <a class="link" @click="toggleFirstLineLock">{{ isFirstLineLocked ? '解锁' : '锁定' }}</a>
            </template>
          </template>
          <template v-else>
            {{ index }}.未激活.<a class="link" @click="unlockLine(index)">激活</a>（钥匙×{{ getUnlockKeyCost(index) }}）
          </template>
        </div>
      </template>
      
      <!-- 洗练消耗信息 -->
      <div class="section">
        消耗灵力：{{ refineCost }}/次
      </div>
      <div class="section">
        拥有灵力：{{ currentSpiritPower }}
      </div>
      
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
.spirit-refine-page {
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
  font-size: 11px;
}
</style>
