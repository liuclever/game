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
  const id = route.query.id
  if (!id) {
    errorMessage.value = '缺少战报ID'
    loading.value = false
    return
  }

  loading.value = true
  errorMessage.value = ''
  try {
    const res = await http.get(`/battlefield/battle/${id}`)
    if (res.data.ok) {
      battleLog.value = res.data.battle
    } else {
      errorMessage.value = res.data.error || '加载战报失败'
    }
  } catch (e) {
    console.error('加载战场战报失败', e)
    errorMessage.value = '加载战报失败'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadBattle()
})

const battlefieldName = computed(() => {
  if (!battleLog.value) return ''
  const t = battleLog.value.battlefield_type
  if (t === 'crane') return '飞鹤战场'
  return '猛虎战场'
})

const isVictory = computed(() => {
  if (!battleLog.value || !battleLog.value.battle_data) return true
  return !!battleLog.value.battle_data.is_victory
})

const resultText = computed(() => {
  if (!battleLog.value) return ''
  return isVictory.value ? '胜利' : '失败'
})

const battles = computed(() => {
  if (!battleLog.value || !battleLog.value.battle_data) return []
  return battleLog.value.battle_data.battles || []
})

const currentBattle = computed(() => {
  const list = battles.value
  if (!list.length) return null
  const index = Math.min(selectedBattleIndex.value, list.length - 1)
  return list[index]
})

const goBack = () => {
  router.back()
}

const goBattlefield = () => {
  router.push('/battlefield')
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="report-page">
    <div class="section title">
      【详细战报】 <a class="link" @click="goBack">返回</a>
    </div>

    <div v-if="loading" class="section">加载中...</div>
    <div v-else-if="errorMessage" class="section red">{{ errorMessage }}</div>

    <template v-else-if="battleLog && battleLog.battle_data">
      <!-- 基本信息 -->
      <div class="section">
        战场：<span class="blue">{{ battlefieldName }}</span> 第{{ battleLog.period }}期
      </div>
      <div class="section">
        轮次：第{{ battleLog.round_num }}轮 比赛{{ battleLog.match_num }}
      </div>
      <div class="section">
        对阵：<span class="blue">{{ battleLog.first_user_name }}</span> VS <span class="orange">{{ battleLog.second_user_name }}</span>
      </div>
      <div class="section">
        结果：<span :class="isVictory ? 'green' : 'red'">{{ resultText }}</span>
      </div>

      <!-- 多战切换 -->
      <div v-if="battles.length > 1" class="section tabs">
        <span
          v-for="(b, idx) in battles"
          :key="idx"
          :class="['tab', { active: idx === selectedBattleIndex }]"
          @click="selectedBattleIndex = idx"
        >
          第{{ b.battle_num || idx + 1 }}战
        </span>
      </div>

      <!-- 回合记录 -->
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
      <a class="link" @click="goBattlefield">返回战场</a>
    </div>
    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>

  </div>
</template>

<style scoped>
.report-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 16px;
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

.link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.blue {
  color: #0066CC;
}

.orange {
  color: #FF6600;
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
  font-size: 17px;
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

.spacer {
  margin-top: 16px;
}

.footer {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #CCCCCC;
}
</style>
