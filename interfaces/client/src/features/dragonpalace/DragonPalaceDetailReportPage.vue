<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import http from '@/services/http'

const route = useRoute()
const router = useRouter()

const battleData = ref(null)
const activeBattleIndex = ref(0)

onMounted(() => {
  // URL 直达：/dragonpalace/detail-report?stage=1&index=0
  const stageRaw = route.query.stage
  const stage = parseInt(String(stageRaw || '0'), 10)
  if (Number.isFinite(stage) && stage > 0) {
    http.get('/dragonpalace/report', { params: { stage } })
      .then((res) => {
        if (res.data?.ok) {
          battleData.value = { battles: res.data.report?.battles || [] }
        } else {
          battleData.value = null
        }
      })
      .catch(() => { battleData.value = null })
      .finally(() => {
        const idxRaw = route.query.index
        const idx = parseInt(String(idxRaw || '0'), 10)
        if (Number.isFinite(idx) && idx >= 0) {
          activeBattleIndex.value = idx
        }
      })
    return
  }

  const state = history.state
  if (state && state.battleData) {
    battleData.value = state.battleData
    return
  }
  const saved = sessionStorage.getItem('currentDragonPalaceBattle')
  if (saved) {
    try {
      const parsed = JSON.parse(saved)
      battleData.value = parsed.battleData || null
    } catch (e) {
      console.error('解析缓存战报失败:', e)
    }
  }
})

const battles = computed(() => {
  if (!battleData.value || !battleData.value.battles) return []
  return battleData.value.battles
})

const currentBattle = computed(() => {
  if (battles.value.length === 0) return null
  return battles.value[activeBattleIndex.value]
})

const selectBattle = (idx) => {
  activeBattleIndex.value = idx
  // 模仿外站“第1战|第2战”可点击跳不同 index 的形式：更新 URL query
  const stage = route.query.stage
  router.replace({ path: '/dragonpalace/detail-report', query: { ...(stage ? { stage } : {}), index: idx } })
}

const goBack = () => {
  router.back()
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="detail-report-page">
    <template v-if="battleData && battles.length > 0">
      <div class="section title">
        【详细战报】<a class="link" @click="goBack">返回</a>
      </div>

      <div class="section">
        <span v-for="(battle, idx) in battles" :key="idx">
          <a
            :class="['link', { 'active': idx === activeBattleIndex }]"
            @click="selectBattle(idx)"
          >第{{ battle.battle_num }}战</a>
          <span v-if="idx < battles.length - 1"> | </span>
        </span>
      </div>

      <template v-if="currentBattle">
        <div v-for="(round, rIdx) in currentBattle.rounds" :key="rIdx" class="section">
          [回合{{ rIdx + 1 }}]：{{ round.action }}
        </div>
        <div class="section">[战斗结束]: {{ currentBattle.result }}</div>
      </template>
    </template>

    <template v-else>
      <div class="section gray">无战斗数据</div>
    </template>

    <div class="section spacer">
      <a class="link" @click="goBack">返回前页</a>
    </div>
    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>
  </div>
</template>

<style scoped>
.detail-report-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 13px;
  line-height: 1.6;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 2px 0;
}

.title {
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

.link.active {
  font-weight: bold;
}

.gray {
  color: #666666;
}
</style>


