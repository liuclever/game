<script setup>
import { useMessage } from '@/composables/useMessage'
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import http from '@/services/http'

const route = useRoute()
const router = useRouter()
const talentKey = computed(() => route.params.key)

const { message, messageType, showMessage } = useMessage()

const loading = ref(true)
const submitting = ref(false)
const overview = ref(null)
const errorMessage = ref('')

const fetchOverview = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const res = await http.get('/alliance/talent')
    if (res.data.ok) {
      overview.value = res.data
    } else {
      errorMessage.value = res.data.error || '获取天赋信息失败'
    }
  } catch (e) {
    errorMessage.value = e.response?.data?.error || '获取天赋信息失败'
  } finally {
    loading.value = false
  }
}

const currentTalent = computed(() => {
  if (!overview.value) return null
  return overview.value.talents.find((t) => t.key === talentKey.value)
})

const allianceResources = computed(() => overview.value?.resources || { funds: 0, crystals: 0 })
const researchCost = computed(() => currentTalent.value?.research_cost || null)

const blockedReason = computed(() => {
  if (!overview.value) return '未获取到天赋信息'
  if (!overview.value.can_research) return '仅盟主可以研发天赋'
  if (!currentTalent.value) return '未找到该天赋'
  if (currentTalent.value.research_level >= overview.value.building_level) return '研究等级已达建筑上限'
  if (researchCost.value) {
    if (allianceResources.value.funds < researchCost.value.funds) return '联盟资金不足'
    if (allianceResources.value.crystals < researchCost.value.crystals) return '焚火晶不足'
  }
  return ''
})

const canResearch = computed(() => !blockedReason.value)

const confirmResearch = async () => {
  if (!canResearch.value || submitting.value) return
  submitting.value = true
  try {
    const res = await http.post('/alliance/talent/research', { talent_key: talentKey.value })
    if (res.data.ok) {
      showMessage('研究成功，天赋上限提升', 'success')
      await fetchOverview()
    } else {
      showMessage(res.data.error || '研究失败', 'error')
    }
  } catch (e) {
    showMessage(e.response?.data?.error || '研究失败', 'error')
  } finally {
    submitting.value = false
  }
}

const goBackPool = () => {
  router.push('/alliance/talent')
}

const goHome = () => {
  router.push('/')
}

onMounted(() => {
  fetchOverview()
})
</script>

<template>
  <div class="talent-detail-page">
    <!-- 消息提示 -->
    <div v-if="message" class="message" :class="messageType">
      {{ message }}
    </div>

    <div v-if="loading" class="section">加载中...</div>
    <template v-else-if="currentTalent">
      <div class="section title">{{ currentTalent.label }}研究</div>
      <div class="section">建筑等级上限：{{ overview.building_level }}级（研究等级不得超过建筑等级）</div>
      <div class="section">
        当前研究等级：{{ currentTalent.research_level }}级；
        当前天赋等级上限：{{ currentTalent.max_level }}级
      </div>
      <div class="section">
        研究后天赋等级上限将提升（不超过建筑等级），盟主可通过研究来提升成员可学习的天赋等级。
      </div>
      <div class="section">
        当前联盟资源：资金 {{ allianceResources.funds }}，焚火晶 {{ allianceResources.crystals }}
      </div>
      <div class="section" v-if="researchCost">
        下一等级研发消耗：资金 {{ researchCost.funds }}，焚火晶 {{ researchCost.crystals }}
      </div>
      <div class="section error" v-if="blockedReason">{{ blockedReason }}</div>
      <div class="section actions">
        <button class="btn" :disabled="!canResearch || submitting" @click="confirmResearch">
          {{ canResearch ? '研究' : '无法研究' }}
        </button>
        <button class="btn secondary" @click="goBackPool">返回天赋池</button>
      </div>
      <div class="section footer-links">
        <a class="link" @click="goBackPool">返回天赋池</a><br>
        <a class="link" @click="goHome">返回游戏首页</a>
      </div>
    </template>
    <div v-else class="section error">
      {{ errorMessage || '未找到该天赋、或您无权研究' }}<br>
      <a class="link" @click="goBackPool">返回天赋池</a>
    </div>
  </div>
</template>

<style scoped>
.talent-detail-page {
  background: #fff8dc;
  min-height: 100vh;
  padding: 12px 18px;
  font-size: 13px;
  line-height: 1.8;
  font-family: SimSun, '宋体', serif;
}

.section {
  margin: 10px 0;
}

.title {
  font-weight: bold;
  font-size: 16px;
}

.actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.btn {
  background: #f5deb3;
  border: 1px solid #c49c48;
  padding: 6px 16px;
  cursor: pointer;
  font-family: inherit;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn.secondary {
  background: #eee2c5;
}

.link {
  color: #0066cc;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.error {
  color: #a00;
}

/* 消息提示样式 */
.message {
  padding: 12px;
  margin: 12px 0;
  border-radius: 4px;
  font-weight: bold;
  text-align: center;
}

.message.success {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.message.error {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.message.info {
  background: #d1ecf1;
  color: #0c5460;
  border: 1px solid #bee5eb;
}

</style>
