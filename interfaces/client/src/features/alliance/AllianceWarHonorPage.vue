<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { fetchWarHonorStatus, postWarHonorExchange } from '@/api/alliance'

const router = useRouter()

const loading = ref(true)
const submitting = ref(false)
const currentHonor = ref(0)
const historicalHonor = ref(0)
const effects = ref([])
const errorMsg = ref('')
const successMsg = ref('')

const goWar = () => {
  router.push('/alliance/war')
}

const goAlliance = () => {
  router.push('/alliance')
}

const goHome = () => {
  router.push('/')
}

const loadHonorStatus = async () => {
  loading.value = true
  errorMsg.value = ''
  successMsg.value = ''
  try {
    const res = await fetchWarHonorStatus()
    if (res?.ok) {
      currentHonor.value = res.data.currentHonor || 0
      historicalHonor.value = res.data.historicalHonor || 0
      effects.value = res.data.effects || []
    } else {
      errorMsg.value = res?.error || '战功信息获取失败'
    }
  } catch (err) {
    errorMsg.value = err?.response?.data?.error || '网络异常，请稍后重试'
  } finally {
    loading.value = false
  }
}

const formatCountdown = (iso) => {
  if (!iso) return ''
  const end = new Date(iso)
  const now = new Date()
  const diffMs = end - now
  if (diffMs <= 0) return '已到期'
  const hours = Math.floor(diffMs / (1000 * 60 * 60))
  const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60))
  return `${hours}小时${minutes}分`
}

const handleExchange = async (effect) => {
  if (!effect?.canExchange || submitting.value) return
  submitting.value = true
  errorMsg.value = ''
  successMsg.value = ''
  try {
    const res = await postWarHonorExchange(effect.key)
    if (res?.ok) {
      successMsg.value = `${effect.name} 兑换成功！`
      await loadHonorStatus()
    } else {
      errorMsg.value = res?.error || '兑换失败'
    }
  } catch (err) {
    errorMsg.value = err?.response?.data?.error || '网络异常，兑换失败'
  } finally {
    submitting.value = false
  }
}

const effectCount = computed(() => effects.value.length)

onMounted(() => {
  loadHonorStatus()
})
</script>

<template>
  <div class="honor-page">
    <div class="section title-row">
      【战功兑换】 <a class="link" @click.prevent="goWar">返回</a>
    </div>

    <div class="section tabs">
      <span class="tab active">联盟战功</span>
    </div>

    <div v-if="loading" class="section">
      正在加载战功信息...
    </div>
    <div v-else class="section values">
      <div>
        当前战功: <span class="blue">{{ currentHonor }}</span>
      </div>
      <div>
        历史战功: <span class="blue">{{ historicalHonor }}</span>
      </div>
    </div>

    <div v-if="errorMsg" class="section warn">
      {{ errorMsg }}
    </div>

    <div v-if="successMsg" class="section success">
      {{ successMsg }}
    </div>

    <div class="section">
      【兑换列表】（共 {{ effectCount }} 项）
    </div>
    <div class="section list-header">
      名称 / 战功消耗
    </div>
    <div v-for="effect in effects" :key="effect.key" class="section effect-row" :class="{ active: effect.active }">
      <div class="effect-main">
        <div class="effect-name">
          {{ effect.name }}
          <span v-if="effect.active" class="badge">生效中</span>
        </div>
        <div class="effect-desc">
          {{ effect.description || '效果持续 1 天' }}
        </div>
        <div v-if="effect.active && effect.expiresAt" class="effect-timer">
          剩余时间：{{ formatCountdown(effect.expiresAt) }}
        </div>
        <div v-else-if="!effect.canExchange && effect.reason" class="effect-reason warn">
          {{ effect.reason }}
        </div>
      </div>
      <div class="effect-actions">
        <div class="cost">消耗战功：{{ effect.cost }}</div>
        <button
          class="exchange-btn"
          :disabled="!effect.canExchange || submitting"
          @click="handleExchange(effect)"
        >
          {{ effect.canExchange ? (submitting ? '兑换中…' : '兑换') : '不可兑换' }}
        </button>
      </div>
    </div>

    <div class="section info-block">
      <div>⚠️ 效果持续 1 天，期间同一效果不可重复兑换。</div>
      <div>⚠️ 经验加成效果互斥，如已有经验加成生效请等待结束后再兑换。</div>
      <div>⚠️ 仅盟主与副盟主可以执行战功兑换。</div>
    </div>

    <div class="section spacer">
      <a class="link" @click.prevent="goWar">返回盟战</a>
    </div>
    <div class="section">
      <a class="link" @click.prevent="goAlliance">返回联盟</a>
    </div>
    <div class="section">
      <a class="link" @click.prevent="goHome">返回游戏首页</a>
    </div>

  </div>
</template>

<style scoped>
.honor-page {
  background: #fff8dc;
  min-height: 100vh;
  padding: 10px 14px 24px;
  font-size: 13px;
  line-height: 1.7;
  font-family: SimSun, '宋体', serif;
}

.section {
  margin: 6px 0;
}

.values {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.title-row {
  font-weight: bold;
  font-size: 15px;
}

.tabs {
  margin-top: 4px;
}

.tab {
  padding: 2px 6px;
  border: 1px solid #d2a94a;
  background: #f9e2a0;
}

.tab.active {
  font-weight: bold;
}

.link {
  color: #0066cc;
  cursor: pointer;
}

.link:hover {
  text-decoration: underline;
}

.blue {
  color: #0066cc;
}

.warn {
  color: #c03;
}

.success {
  color: #0a840a;
}

.gray {
  color: #777;
}

.small {
  font-size: 11px;
}

.footer {
  margin-top: 20px;
}

.spacer {
  margin-top: 16px;
}

.list-header {
  font-weight: bold;
  border-bottom: 1px solid #d2a94a;
  padding-bottom: 4px;
}

.effect-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  border-bottom: 1px dashed #d8c48a;
  padding-bottom: 8px;
}

.effect-row:last-of-type {
  border-bottom: none;
}

.effect-row.active .effect-name {
  color: #c03;
  font-weight: bold;
}

.effect-main {
  flex: 1;
}

.effect-name {
  font-size: 14px;
}

.effect-desc,
.effect-timer,
.effect-reason {
  font-size: 12px;
}

.badge {
  display: inline-block;
  margin-left: 6px;
  padding: 1px 4px;
  border: 1px solid #c03;
  color: #c03;
  font-size: 11px;
}

.effect-actions {
  min-width: 120px;
  text-align: right;
}

.cost {
  font-size: 12px;
  margin-bottom: 6px;
}

.exchange-btn {
  padding: 4px 10px;
  border: 1px solid #0a6abf;
  background: #1084e3;
  color: #fff;
  cursor: pointer;
  font-size: 12px;
}

.exchange-btn:disabled {
  background: #ccc;
  border-color: #aaa;
  cursor: not-allowed;
}

.info-block {
  background: #fff3d6;
  border: 1px solid #e0c88f;
  padding: 8px;
  font-size: 12px;
  line-height: 1.5;
}
</style>
