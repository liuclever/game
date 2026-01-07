<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const battleData = ref(null)

const loadBattleData = () => {
  try {
    const dataStr = route.query.data
    if (dataStr) {
      battleData.value = JSON.parse(dataStr)
    }
  } catch (e) {
    console.error('解析战报数据失败', e)
  }
}

const resultText = computed(() => {
  if (!battleData.value) return ''
  return battleData.value.is_victory ? '胜利' : '失败'
})

const resultClass = computed(() => {
  if (!battleData.value) return ''
  return battleData.value.is_victory ? 'green' : 'red'
})

const goBack = () => {
  router.back()
}

const goHome = () => {
  router.push('/')
}

onMounted(() => {
  loadBattleData()
})
</script>

<template>
  <div class="report-page">
    <div class="section title">【切磋战报】</div>

    <template v-if="battleData">
      <div class="section">
        对手: <span class="orange">{{ battleData.defender_name }}</span>
      </div>
      <div class="section">
        结果: <span :class="resultClass">{{ resultText }}</span>
      </div>
      <div class="section">总回合数: {{ battleData.total_turns }}</div>

      <div class="section title2">【战斗过程】</div>
      
      <template v-for="(battle, bIdx) in battleData.battles" :key="bIdx">
        <div class="section battle-header">
          第{{ battle.battle_num }}场战斗
          <span v-if="battle.result" class="result-text">
            → {{ battle.result }}
          </span>
        </div>
        
        <div class="round-list">
          <div 
            v-for="(round, rIdx) in battle.rounds" 
            :key="rIdx"
            class="section round-item"
          >
            <span class="round-num">[回合{{ round.round }}]</span>
            <span class="action-text">{{ round.action }}</span>
          </div>
        </div>
      </template>
    </template>

    <div v-else class="section">暂无战报数据</div>

    <div class="nav-links">
      <div><a class="link" @click="goBack">返回前页</a></div>
      <div><a class="link" @click="goHome">返回游戏首页</a></div>
    </div>

    
  </div>
</template>

<style scoped>
.report-page {
  background: #FFF8DC;
  min-height: 100vh;
  padding: 10px 12px;
  font-size: 14px;
  line-height: 1.8;
  font-family: SimSun, "宋体", serif;
}

.title {
  font-weight: bold;
  color: #333;
}

.title2 {
  font-weight: bold;
  margin-top: 15px;
}

.section {
  margin: 4px 0;
}

.battle-header {
  font-weight: bold;
  margin-top: 12px;
  color: #333;
}

.result-text {
  font-weight: normal;
  color: #666;
}

.round-list {
  margin-left: 8px;
}

.round-item {
  margin: 2px 0;
}

.round-num {
  color: #0066CC;
  margin-right: 4px;
}

.action-text {
  color: #333;
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

.green {
  color: #009900;
}

.red {
  color: #CC0000;
}

.gray {
  color: #666;
}

.nav-links {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #ccc;
}

.footer {
  margin-top: 20px;
}

.small {
  font-size: 11px;
}
</style>
