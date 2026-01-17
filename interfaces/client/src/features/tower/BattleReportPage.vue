<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()

// ========== 玩家信息（从后端加载） ==========
const playerName = ref('')

// 从路由参数获取层数和塔类型
const floor = ref(parseInt(route.query.floor) || 1)
const towerType = computed(() => route.query.type || 'tongtian')

// 塔名称映射
const towerNames = {
  tongtian: '通天塔',
  longwen: '龙纹塔',
  zhanling: '战灵塔',
}
const towerNameDisplay = computed(() => towerNames[towerType.value] || '通天塔')

// 战斗数据
const battleData = ref(null)
const isVictory = ref(true)

// 敌方信息
const guardians = ref([])

// 参战的幻兽
const beastsUsed = ref([])

// 战斗回合记录
const rounds = ref([])

// 分页相关
const currentPage = ref(1)
const roundsPerPage = 10

// 塔层名称
const towerName = computed(() => {
  return `${towerNameDisplay.value}${floor.value}层`
})

// 最后参战的玩家幻兽
const lastPlayerBeast = computed(() => {
  if (beastsUsed.value.length > 0) {
    return beastsUsed.value[beastsUsed.value.length - 1]
  }
  return '圣灵蚁-神界'
})

// 最后的守塔幻兽
const lastGuardian = computed(() => {
  if (guardians.value.length > 0) {
    return guardians.value[guardians.value.length - 1]
  }
  return { name: '远古谜兽', level: 1 }
})

// 获胜方剩余气血（从最后一条战报记录中获取）
const winnerRemainingHp = computed(() => {
  if (rounds.value.length === 0) return 0
  const lastRound = rounds.value[rounds.value.length - 1]
  // 如果玩家胜利，返回攻击方的剩余气血（因为最后一击是玩家打死守护兽）
  // 如果玩家失败，返回防守方的剩余气血
  if (isVictory.value) {
    // 玩家胜利，最后一击是玩家攻击，attacker_hp是玩家幻兽的剩余HP
    return lastRound.attacker_hp_after || lastRound.attacker_hp || 0
  } else {
    // 玩家失败，最后一击是守护兽攻击，attacker_hp是守护兽的剩余HP
    return lastRound.attacker_hp_after || lastRound.attacker_hp || 0
  }
})

// 总页数
const totalPages = computed(() => {
  return Math.ceil(rounds.value.length / roundsPerPage)
})

// 当前页的回合
const currentRounds = computed(() => {
  const start = (currentPage.value - 1) * roundsPerPage
  const end = start + roundsPerPage
  return rounds.value.slice(start, end)
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

// 加载战斗数据
onMounted(async () => {
  // 加载玩家信息
  try {
    const playerRes = await http.get('/player/info')
    if (playerRes.data.ok) {
      playerName.value = playerRes.data.player.nickname || `玩家${playerRes.data.player.userId}`
    }
  } catch (e) {
    console.error('加载玩家信息失败', e)
  }

  const data = sessionStorage.getItem('currentBattle')
  if (data) {
    try {
      battleData.value = JSON.parse(data)
      floor.value = battleData.value.floor
      isVictory.value = battleData.value.is_victory
      guardians.value = battleData.value.guardians || []
      beastsUsed.value = battleData.value.beasts_used || []

      // 使用后端提供的详细回合描述（包含扣血数值）
      const rawRounds = battleData.value.rounds || []
      rounds.value = rawRounds.map(r => ({
        round_num: r.round_num || r.round,
        description: r.description || r.action,
        attacker_hp_after: r.attacker_hp_after || r.attacker_hp,
        defender_hp_after: r.defender_hp_after || r.defender_hp,
        damage: r.damage || 0,
      }))
    } catch (e) {
      console.error('解析战斗数据失败', e)
    }
  }
})

// ========== 导航 ==========
const goBack = () => {
  router.back()
}

const goTower = () => {
  router.push('/tower')
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="report-page">
    <!-- 标题 -->
    <div class="section title">
      【详细战报】 <a class="link" @click="goBack">返回</a>
    </div>

    <!-- 轮次 -->
    <div class="section">第1轮</div>

    <!-- 分页导航（顶部） -->
    <div v-if="totalPages > 1" class="section pagination">
      <a v-if="hasPrevPage" class="link" @click="prevPage">上一页</a>
      <span v-else class="gray">上一页</span>
      <span class="page-info">第{{ currentPage }}/{{ totalPages }}页</span>
      <a v-if="hasNextPage" class="link" @click="nextPage">下一页</a>
      <span v-else class="gray">下一页</span>
    </div>

    <!-- 当前页的回合记录 -->
    <div v-for="r in currentRounds" :key="r.round_num" class="section">
      [回合{{ r.round_num }}]: {{ r.description }}
    </div>

    <!-- 战斗结果（最后一页显示） -->
    <div v-if="currentPage === totalPages" class="section result">
      <template v-if="isVictory">
        [战斗结束]: 『<span class="tower-name">{{ towerName }}</span>』的{{ lastGuardian.name }}阵亡，『<span class="player-name">{{ playerName }}</span>』的<span class="beast-name">{{ lastPlayerBeast }}</span>剩余气血{{ winnerRemainingHp }}
      </template>
      <template v-else>
        [战斗结束]: 『<span class="player-name">{{ playerName }}</span>』的<span class="beast-name">{{ lastPlayerBeast }}</span>阵亡，『<span class="tower-name">{{ towerName }}</span>』的{{ lastGuardian.name }}剩余气血{{ winnerRemainingHp }}
      </template>
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

    <!-- 导航 -->
    <div class="section spacer">
      <a class="link" @click="goBack">返回前页</a>
    </div>
    <div class="section">
      <a class="link" @click="goTower">返回闯塔首页</a>
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
  margin: 2px 0;
}

.title {
  margin-bottom: 8px;
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

.player-name {
  color: #0066CC;
}

.beast-name {
  color: #0066CC;
}

.tower-name {
  color: #0066CC;
}

.result {
  margin-top: 12px;
  padding-top: 8px;
  border-top: 1px solid #EEEEEE;
}

.gray {
  color: #999999;
}

.small {
  font-size: 17px;
}

.footer {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #CCCCCC;
}
</style>
