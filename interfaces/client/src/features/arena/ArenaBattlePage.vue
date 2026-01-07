<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()

const loading = ref(true)
const errorMessage = ref('')
const battleLog = ref(null)
const selectedBattleIndex = ref(0)

const loadBattle = async () => {
  const battleId = route.query.id
  if (!battleId) {
    errorMessage.value = '缺少战报ID'
    loading.value = false
    return
  }

  try {
    const res = await http.get(`/arena/battle/${battleId}`)
    if (res.data.ok) {
      battleLog.value = res.data.battle
    } else {
      errorMessage.value = res.data.error || '战报加载失败'
    }
  } catch (e) {
    console.error('加载擂台战报失败', e)
    errorMessage.value = '战报加载失败'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadBattle()
})

const arenaTypeName = computed(() => {
  if (!battleLog.value) return ''
  return battleLog.value.arena_type === 'gold' ? '黄金场' : '普通场'
})

const isVictory = computed(() => {
  if (!battleLog.value || !battleLog.value.battle_data) return true
  return !!battleLog.value.battle_data.is_victory
})

const resultText = computed(() => {
  if (!battleLog.value) return ''
  return isVictory.value ? '挑战成功' : '挑战失败'
})

const currentBattle = computed(() => {
  if (!battleLog.value || !battleLog.value.battle_data) return null
  const battles = battleLog.value.battle_data.battles || []
  if (!battles.length) return null
  const index = Math.min(selectedBattleIndex.value, battles.length - 1)
  return battles[index]
})

const goBack = () => {
  router.back()
}

const goArena = () => {
  router.push('/arena')
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="report-page">
    <!-- 标题 -->
    <div class="section title">
      【擂台战报】 <a class="link" @click="goBack">返回</a>
    </div>

    <div v-if="loading" class="section">加载中...</div>
    <div v-else-if="errorMessage" class="section red">{{ errorMessage }}</div>

    <template v-else-if="battleLog && battleLog.battle_data">
      <!-- 基本信息 -->
      <div class="section">
        场次：<span class="orange">{{ arenaTypeName }}</span> {{ battleLog.rank_name }}
      </div>
      <div class="section">
        挑战者：<span class="blue">{{ battleLog.challenger_name }}</span>
      </div>
      <div class="section">
        擂主：<span class="blue">{{ battleLog.champion_name }}</span>
      </div>
      <div class="section">
        结果：<span :class="isVictory ? 'green' : 'red'">{{ resultText }}</span>
      </div>

      <!-- 战斗过程 -->
      <div class="section title2">【战斗过程】</div>

      <!-- 多战切换标签 -->
      <div
        v-if="battleLog.battle_data.battles && battleLog.battle_data.battles.length > 1"
        class="section tabs"
      >
        <span
          v-for="(b, idx) in battleLog.battle_data.battles"
          :key="idx"
          :class="['tab', { active: idx === selectedBattleIndex }]"
          @click="selectedBattleIndex = idx"
        >
          第{{ b.battle_num || idx + 1 }}战
        </span>
      </div>

      <!-- 当前战的回合记录 -->
      <template v-if="currentBattle">
        <div class="section">
          第{{ currentBattle.battle_num || selectedBattleIndex + 1 }}战
        </div>
        <div
          v-for="r in currentBattle.rounds || []"
          :key="r.round"
          class="section"
        >
          [回合{{ r.round }}]: {{ r.action }}
        </div>
        <div class="section result-line">
          [战斗结束]: {{ currentBattle.result }}
        </div>
      </template>
    </template>

    <!-- 导航 -->
    <div class="section spacer">
      <a class="link" @click="goArena">返回擂台</a>
    </div>
    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>

  </div>
</template>

<style scoped>
.report-page {
  background: #FFF8DC;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 13px;
  line-height: 1.6;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 4px 0;
}

.title {
  font-weight: bold;
  margin-bottom: 8px;
}

.title2 {
  font-weight: bold;
  margin-top: 12px;
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

.orange {
  color: #FF6600;
}

.blue {
  color: #0066CC;
}

.green {
  color: #009900;
}

.red {
  color: #CC0000;
}

.gray {
  color: #666666;
}

.small {
  font-size: 11px;
}

.tabs {
  margin-top: 4px;
}

.tab {
  display: inline-block;
  margin-right: 8px;
  padding: 2px 6px;
  border: 1px solid #ccc;
  border-radius: 3px;
  cursor: pointer;
}

.tab.active {
  background: #FFFAE0;
  border-color: #FF6600;
  color: #FF6600;
}

.result-line {
  margin-top: 6px;
}

.footer {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #CCCCCC;
}
</style>
