<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()

// 战斗数据
const battle = ref(null)
const loading = ref(true)
const error = ref('')

// 当前显示的战斗（第几战）
const currentBattle = ref(0)

// 回合分页（每页10条记录）
const currentPage = ref(1)
const pageSize = 10

// 加载战斗详情
const loadBattle = async () => {
  const battleId = route.query.id
  if (!battleId) {
    error.value = '无效的战斗ID'
    loading.value = false
    return
  }
  
  try {
    const res = await http.get(`/zhenyao/battle/${battleId}`)
    if (res.data.ok) {
      battle.value = res.data.battle
    } else {
      error.value = res.data.error
    }
  } catch (e) {
    console.error('加载战斗详情失败', e)
    error.value = '加载失败'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadBattle()
})

// 战斗列表
const battles = computed(() => {
  if (!battle.value || !battle.value.battle_data) return []
  return battle.value.battle_data.battles || []
})

// 当前战斗详情
const currentBattleDetail = computed(() => {
  if (battles.value.length === 0) return null
  return battles.value[currentBattle.value]
})

// 当前战斗的分页回合列表
const pagedRounds = computed(() => {
  const detail = currentBattleDetail.value
  if (!detail || !detail.rounds) return []
  const start = (currentPage.value - 1) * pageSize
  return detail.rounds.slice(start, start + pageSize)
})

// 总页数
const totalPages = computed(() => {
  const detail = currentBattleDetail.value
  if (!detail || !detail.rounds) return 1
  return Math.max(1, Math.ceil(detail.rounds.length / pageSize))
})

// 切换战斗
const switchBattle = (index) => {
  currentBattle.value = index
  currentPage.value = 1
}

// 分页控制
const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}

// 返回镇妖页
const goBack = () => {
  router.push('/tower/zhenyao')
}

// 返回首页
const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="battle-page">
    <!-- 标题 -->
    <div class="section title">
      【详细战报】 <a class="link" @click="goBack">返回</a>
    </div>

    <!-- 加载中 -->
    <div v-if="loading" class="section gray">加载中...</div>

    <!-- 错误 -->
    <div v-else-if="error" class="section red">{{ error }}</div>

    <!-- 战斗内容 -->
    <template v-else-if="battle">
      <!-- 战斗切换标签 -->
      <div class="section">
        <template v-for="(b, index) in battles" :key="index">
          <a 
            class="link battle-tab" 
            :class="{ active: currentBattle === index }"
            @click="switchBattle(index)"
          >第{{ index + 1 }}战</a>
          <span v-if="index < battles.length - 1"> | </span>
        </template>
      </div>

      <!-- 战斗详情 -->
      <template v-if="currentBattleDetail">
        <!-- 回合列表（分页，每页10条） -->
        <div 
          v-for="(round, idx) in pagedRounds" 
          :key="idx" 
          class="section round"
        >
          [回合{{ round.round }}]：{{ round.action }}
        </div>

        <!-- 回合分页导航 -->
        <div v-if="totalPages > 1" class="section">
          第{{ currentPage }}/{{ totalPages }}页
          <a class="link" @click="prevPage">上页</a>
          <a class="link" @click="nextPage">下页</a>
        </div>

        <!-- 战斗结果 -->
        <div class="section result">
          战斗结束：{{ currentBattleDetail.result }}
        </div>
      </template>

      <!-- 总体结果 -->
      <div class="section summary">
        <span v-if="battle.is_success" class="green bold">
          {{ battle.attacker_name }} 抢夺第{{ battle.floor }}层成功！
        </span>
        <span v-else class="red bold">
          {{ battle.attacker_name }} 挑战第{{ battle.floor }}层失败！
        </span>
      </div>
    </template>

    <!-- 返回链接 -->
    <div class="section spacer">
      <a class="link" @click="goBack">返回前页</a>
    </div>
    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>

  </div>
</template>

<style scoped>
.battle-page {
  background: #ffffff;
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
  margin-bottom: 12px;
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

.link.active,
.battle-tab.active {
  color: #CC3300;
  font-weight: bold;
}

.gray {
  color: #666666;
}

.red {
  color: #CC0000;
}

.green {
  color: #009900;
}

.bold {
  font-weight: bold;
}

.small {
  font-size: 11px;
}

.round {
  font-size: 12px;
  padding: 2px 0;
}

.result {
  margin-top: 8px;
  font-weight: bold;
}

.summary {
  margin-top: 12px;
  padding: 8px;
  background: #ffffff;
  border: 1px solid #DDD;
}

.footer {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #CCCCCC;
}
</style>
