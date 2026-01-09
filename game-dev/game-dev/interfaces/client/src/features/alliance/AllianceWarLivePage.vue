<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { fetchWarLiveFeed } from '@/api/alliance'

const router = useRouter()
const loading = ref(true)
const error = ref('')
const battles = ref([])

const phaseLabels = {
  0: '等待开战',
  1: '战斗进行中',
  2: '战斗已结束',
}

const loadLiveFeed = async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await fetchWarLiveFeed()
    if (res?.ok) {
      battles.value = res.data?.battles || []
    } else {
      error.value = res?.error || '获取盟战直播失败'
    }
  } catch (err) {
    console.error('加载盟战直播失败', err)
    error.value = err?.response?.data?.error || '获取盟战直播失败'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadLiveFeed()
})

const gotoLandDetail = (landId) => {
  router.push(`/alliance/war/land/${landId}`)
}
</script>

<template>
  <div class="live-page">
    <div class="section title-row">盟战直播</div>
    <div class="section intro">实时查看本联盟正在进行的土地战斗</div>

    <div v-if="loading" class="section">加载中...</div>
    <div v-else-if="error" class="section red">{{ error }}</div>
    <div v-else class="section battles">
      <template v-if="battles.length">
        <div
          v-for="battle in battles"
          :key="battle.battle_id"
          class="battle-card"
        >
          <div class="battle-header">
            <div class="land-name">{{ battle.land_name }}</div>
            <div class="result">{{ battle.result }}</div>
          </div>
          <div class="battle-row">对手联盟：<span class="blue">{{ battle.opponent_alliance_name }}</span></div>
          <div class="battle-row">
            阶段：<span class="orange">{{ phaseLabels[battle.phase] || `阶段${battle.phase}` }}</span>
          </div>
          <div class="battle-row">
            当前回合：<span class="blue">{{ battle.current_round || 1 }}</span>
          </div>
          <div class="battle-actions">
            <button class="detail-btn" @click="gotoLandDetail(battle.land_id)">
              查看战况
            </button>
          </div>
        </div>
      </template>
      <div v-else class="empty">暂无对战记录</div>
    </div>
  </div>
</template>

<style scoped>
.live-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 12px 16px 20px;
  font-size: 13px;
  line-height: 1.5;
  font-family: 'SimSun', '宋体', serif;
  color: #000;
}

.section {
  margin: 8px 0;
}

.title-row {
  font-weight: bold;
  font-size: 16px;
}

.intro {
  color: #555;
}

.battles {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.battle-card {
  border: 1px solid #d8d8d8;
  border-radius: 4px;
  padding: 10px 12px;
  background: #fdfbf7;
}

.battle-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  margin-bottom: 6px;
}

.land-name {
  font-size: 14px;
}

.result {
  color: #cc6600;
}

.battle-row {
  margin: 2px 0;
}

.battle-actions {
  margin-top: 6px;
  text-align: right;
}

.detail-btn {
  background: #fff;
  border: 1px solid #0066cc;
  color: #0066cc;
  padding: 4px 10px;
  border-radius: 4px;
  cursor: pointer;
  font-family: inherit;
}

.detail-btn:hover {
  background: #0066cc;
  color: #fff;
}

.blue {
  color: #0066cc;
}

.orange {
  color: #cc6600;
}

.red {
  color: #cc0000;
}

.empty {
  text-align: center;
  color: #777;
  padding: 20px 0;
}
</style>
