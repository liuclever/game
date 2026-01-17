<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()

const loading = ref(true)
const battleReport = ref(null)

// 加载战报
const loadBattleReport = async () => {
  const battleId = route.query.id
  if (!battleId) {
    battleReport.value = {
      result: '胜利',
      opponent: '月挽星回べう',
      opponentGuild: '切磋匠天門ゞ',
      rounds: [
        { round: 1, myBeast: '火焰龙', myHp: 1000, opBeast: '冰霜虎', opHp: 800, winner: 'me', damage: 250 },
        { round: 2, myBeast: '火焰龙', myHp: 750, opBeast: '雷电鹰', opHp: 600, winner: 'me', damage: 300 },
        { round: 3, myBeast: '火焰龙', myHp: 450, opBeast: '暗影狼', opHp: 700, winner: 'opponent', damage: 450 },
        { round: 4, myBeast: '水晶兽', myHp: 900, opBeast: '暗影狼', opHp: 350, winner: 'me', damage: 350 },
      ],
      winsChange: '+1',
      energyCost: 100,
    }
    loading.value = false
    return
  }
  
  try {
    const res = await http.get(`/pvp/battle_report?id=${battleId}`)
    if (res.data.ok) {
      battleReport.value = res.data.report
    }
  } catch (e) {
    console.error('加载战报失败', e)
  }
  loading.value = false
}

// 返回竞技场
const goBack = () => {
  router.push('/pvp')
}

// 返回首页
const goHome = () => {
  router.push('/')
}

onMounted(() => {
  loadBattleReport()
})
</script>

<template>
  <div class="report-page">
    <!-- 标题 -->
    <div class="section title">【切磋战报】</div>

    <div v-if="loading" class="section">加载中...</div>
    <template v-else-if="battleReport">
      <!-- 战斗结果 -->
      <div class="section">
        对手: 
        <template v-if="battleReport.opponentGuild">
          <span class="orange">{{ battleReport.opponentGuild }}</span>丨
        </template>
        <span class="orange">{{ battleReport.opponent }}</span>
      </div>
      <div class="section">
        结果: <span :class="battleReport.result === '胜利' ? 'green' : 'red'">{{ battleReport.result }}</span>
      </div>
      <div class="section">连胜次数变化: {{ battleReport.winsChange }}</div>
      <div class="section">消耗活力: {{ battleReport.energyCost }}</div>

      <!-- 战斗回合 -->
      <div class="section title2">【战斗过程】</div>
      <div class="section" v-for="r in battleReport.rounds" :key="r.round">
        第{{ r.round }}回合: 
        <span class="blue">{{ r.myBeast }}</span>({{ r.myHp }}) vs 
        <span class="orange">{{ r.opBeast }}</span>({{ r.opHp }}) 
        → <span :class="r.winner === 'me' ? 'green' : 'red'">
          {{ r.winner === 'me' ? '我方胜' : '对方胜' }}
        </span>
        (伤害:{{ r.damage }})
      </div>
    </template>

    <!-- 返回 -->
    <div class="nav-links">
      <div><a class="link" @click="goBack">返回连胜竞技场</a></div>
      <div><a class="link" @click="goHome">返回游戏首页</a></div>
    </div>

  </div>
</template>

<style scoped>
.report-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 10px 12px;
  font-size: 17px;
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
  font-size: 17px;
}
</style>
