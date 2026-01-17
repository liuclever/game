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

// 分页相关
const currentPage = ref(1)
const roundsPerPage = 10

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

// 当前战斗的所有回合
const allRounds = computed(() => {
  if (!currentBattle.value) return []
  return currentBattle.value.rounds || []
})

// 总页数
const totalPages = computed(() => {
  return Math.ceil(allRounds.value.length / roundsPerPage)
})

// 当前页的回合
const currentRounds = computed(() => {
  const start = (currentPage.value - 1) * roundsPerPage
  const end = start + roundsPerPage
  return allRounds.value.slice(start, end)
})

// 是否有上一页
const hasPrevPage = computed(() => currentPage.value > 1)

// 是否有下一页
const hasNextPage = computed(() => currentPage.value < totalPages.value)

// 上一页
const prevPage = () => {
  if (hasPrevPage.value) {
    currentPage.value--
  }
}

// 下一页
const nextPage = () => {
  if (hasNextPage.value) {
    currentPage.value++
  }
}

// 跳转到指定页
const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

// 切换战斗时重置页码
const switchBattle = (index) => {
  selectedBattleIndex.value = index
  currentPage.value = 1
}

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
          @click="switchBattle(idx)"
        >
          第{{ b.battle_num || idx + 1 }}战
        </span>
      </div>

      <!-- 当前战的回合记录 -->
      <template v-if="currentBattle">
        <div class="section">
          第{{ currentBattle.battle_num || selectedBattleIndex + 1 }}战
        </div>

        <!-- 分页导航（顶部） -->
        <div v-if="totalPages > 1" class="section pagination">
          <a v-if="hasPrevPage" class="link" @click="prevPage">上一页</a>
          <span v-else class="gray">上一页</span>
          <span class="page-info">第{{ currentPage }}/{{ totalPages }}页</span>
          <a v-if="hasNextPage" class="link" @click="nextPage">下一页</a>
          <span v-else class="gray">下一页</span>
        </div>

        <!-- 当前页的回合 -->
        <div
          v-for="r in currentRounds"
          :key="r.round"
          class="section"
        >
          [回合{{ r.round }}]: {{ r.action }}
        </div>

        <!-- 战斗结果（最后一页显示） -->
        <div v-if="currentPage === totalPages" class="section result-line">
          [战斗结束]: {{ currentBattle.result }}
        </div>

        <!-- 分页导航（底部） -->
        <div v-if="totalPages > 1" class="section pagination">
          <a v-if="hasPrevPage" class="link" @click="prevPage">上一页</a>
          <span v-else class="gray">上一页</span>
          <span class="page-info">第{{ currentPage }}/{{ totalPages }}页</span>
          <a v-if="hasNextPage" class="link" @click="nextPage">下一页</a>
          <span v-else class="gray">下一页</span>
        </div>

        <!-- 页码快速跳转 -->
        <div v-if="totalPages > 1" class="section page-numbers">
          跳转到：
          <template v-for="page in totalPages" :key="page">
            <a 
              v-if="page !== currentPage" 
              class="link page-num" 
              @click="goToPage(page)"
            >{{ page }}</a>
            <span v-else class="current-page">{{ page }}</span>
          </template>
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

.title2 {
  font-weight: bold;
  margin-top: 12px;
}

.pagination {
  margin: 12px 0;
  padding: 8px 0;
  border-top: 1px solid #EEEEEE;
  border-bottom: 1px solid #EEEEEE;
}

.page-info {
  margin: 0 12px;
  color: #333333;
}

.page-numbers {
  margin: 8px 0;
}

.page-num {
  margin: 0 4px;
}

.current-page {
  margin: 0 4px;
  color: #CC3300;
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

.footer {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #CCCCCC;
}
</style>
