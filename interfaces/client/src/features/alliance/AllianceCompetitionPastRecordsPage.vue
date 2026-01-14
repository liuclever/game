<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()

const loading = ref(true)
const errorMessage = ref('')
const records = ref(null)
const selectedTeam = ref(null)

const zones = [
  { name: '犊虎区', key: 'calf_tiger' },
  { name: '白虎区', key: 'white_tiger' },
  { name: '青龙区', key: 'azure_dragon' },
  { name: '朱雀区', key: 'vermillion_bird' },
  { name: '玄武区', key: 'black_tortoise' },
  { name: '战神区', key: 'god_of_war' },
]

const fetchRecords = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const session = route.query.session || null
    const params = session ? { session } : {}
    const res = await http.get('/alliance/competition/past-records', { params })
    if (res.data?.ok) {
      records.value = res.data
      // 默认选择第一个有战斗记录的战队，如果没有则选择第一个区域（犊虎区）
      if (records.value.battles_by_team && Object.keys(records.value.battles_by_team).length > 0) {
        selectedTeam.value = Object.keys(records.value.battles_by_team)[0]
      } else {
        // 如果没有战斗记录，默认选择第一个区域
        selectedTeam.value = zones[0].key
      }
    } else {
      errorMessage.value = res.data?.error || '获取往届战绩失败'
    }
  } catch (err) {
    console.error('获取往届战绩失败', err)
    errorMessage.value = err.response?.data?.error || '网络错误，请稍后重试'
  } finally {
    loading.value = false
  }
}

const getTeamName = (teamKey) => {
  const team = zones.find(z => z.key === teamKey)
  return team ? team.name.replace('区', '队') : teamKey
}

const getRoundText = (round) => {
  const roundMap = {
    1: '第1轮',
    2: '第2轮',
    3: '第3轮',
    4: '第4轮',
  }
  return roundMap[round] || `第${round}轮`
}

const getResultText = (isWin) => {
  return isWin ? '胜' : '负'
}

const viewBattle = (battleId) => {
  // TODO: 实现查看战斗详情
  alert(`查看战斗详情: ${battleId}`)
}

const goToCompetition = () => {
  router.push('/alliance/competition')
}

const goToAlliance = () => {
  router.push('/alliance')
}

const goHome = () => {
  router.push('/')
}

onMounted(() => {
  fetchRecords()
})
</script>

<template>
  <div class="past-records-page">
    <div v-if="loading">加载中...</div>
    <div v-else-if="errorMessage" class="error">{{ errorMessage }}</div>
    <template v-else-if="records">
      <div class="section title-row">
        【争霸赛往届战绩】
      </div>
      <div class="section">
        第{{ records.session || '2026-01-11' }}届
      </div>
      
      <div class="section" v-if="records.alliance_rank">
        <div class="record-item">
          联盟战绩: 本届威望{{ records.alliance_prestige }},第{{ records.alliance_rank }}名
        </div>
      </div>
      
      <div class="section" v-if="records.team_records && records.team_records.length > 0">
        <div class="subtitle">[战队战绩]</div>
        <div 
          v-for="team in records.team_records" 
          :key="team.team_key"
          class="record-item"
        >
          {{ team.honor_text }}
        </div>
      </div>
      
      <div class="section" v-if="records.elite_top8_count > 0">
        <div class="subtitle">[精英战绩]</div>
        <div class="record-item">
          本届{{ records.elite_top8_count }}名精英进入8强
        </div>
      </div>
      
      <div class="section">
        <div class="team-tabs">
          <template v-for="(zone, index) in zones" :key="zone.key">
            <a
              class="link tab"
              :class="{ active: selectedTeam === zone.key }"
              @click="selectedTeam = zone.key"
            >
              {{ zone.name }}
            </a>
            <span v-if="index < zones.length - 1" class="tab-separator">|</span>
          </template>
        </div>
        
        <div 
          v-if="selectedTeam && records.battles_by_team && records.battles_by_team[selectedTeam] && records.battles_by_team[selectedTeam].length > 0"
          class="battle-list"
        >
          <div
            v-for="battle in records.battles_by_team[selectedTeam]"
            :key="battle.id"
            class="battle-item"
          >
            {{ getRoundText(battle.round) }},{{ getTeamName(selectedTeam) }}({{ getResultText(battle.is_win) }})VS
            {{ battle.opponent_alliance_name }},
            <a class="link" @click="viewBattle(battle.id)">查看</a>
          </div>
        </div>
        <div v-else-if="selectedTeam" class="no-battles">
          该战队暂无战斗记录
        </div>
      </div>
      
      <div class="section spacer">
        <a class="link" @click="goToAlliance">返回联盟</a>
      </div>
      <div class="section">
        <a class="link" @click="goToCompetition">返回争霸赛</a>
      </div>
      <div class="section">
        <a class="link" @click="goHome">返回游戏首页</a>
      </div>
    </template>
  </div>
</template>

<style scoped>
.past-records-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 10px 14px 24px;
  font-size: 16px;
  line-height: 1.7;
  font-family: SimSun, '宋体', serif;
}

.section {
  margin: 8px 0;
}

.title-row {
  font-weight: bold;
  font-size: 18px;
}

.subtitle {
  font-weight: bold;
  margin-bottom: 4px;
}

.record-item {
  margin: 4px 0;
}

.error {
  color: #b94a48;
}

.link {
  color: #0066cc;
  cursor: pointer;
}

.link:hover {
  text-decoration: underline;
}

.team-tabs {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0;
  margin: 12px 0;
  padding: 8px 0;
}

.tab {
  padding: 2px 4px;
  color: #0066cc;
  cursor: pointer;
  text-decoration: none;
}

.tab:hover {
  text-decoration: underline;
}

.tab.active {
  color: #0066cc;
  font-weight: bold;
}

.tab-separator {
  color: #666;
  margin: 0 4px;
  user-select: none;
}

.battle-list {
  margin-top: 12px;
}

.battle-item {
  margin: 6px 0;
  padding: 4px 0;
  line-height: 1.8;
}

.no-battles {
  color: #999;
  margin: 12px 0;
  font-style: italic;
}

.spacer {
  margin-top: 16px;
}
</style>
