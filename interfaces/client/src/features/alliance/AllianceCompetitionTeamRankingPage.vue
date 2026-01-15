<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()
const loading = ref(true)
const rankingData = ref(null)
const errorMsg = ref('')

const zones = [
  { name: '犊虎区', key: 'calf_tiger' },
  { name: '白虎区', key: 'white_tiger' },
  { name: '青龙区', key: 'azure_dragon' },
  { name: '朱雀区', key: 'vermillion_bird' },
  { name: '玄武区', key: 'black_tortoise' },
  { name: '战神区', key: 'god_of_war' },
]

const stages = [
  { name: '冠军', key: 'champion' },
  { name: '2强', key: 'final' },
  { name: '4强', key: 'semi' },
  { name: '8强', key: 'quarter' },
]

const currentZone = ref(route.query.zone || 'calf_tiger')
const currentStage = ref(route.query.stage || 'all')

const fetchRanking = async () => {
  loading.value = true
  errorMsg.value = ''
  try {
    const res = await http.get(`/alliance/competition/team-ranking?zone=${currentZone.value}&stage=${currentStage.value}`)
    if (res.data?.ok) {
      rankingData.value = res.data
    } else {
      errorMsg.value = res.data?.error || '获取排行榜失败'
    }
  } catch (err) {
    console.error('获取排行榜失败', err)
    errorMsg.value = err.response?.data?.error || '网络错误，请稍后重试'
  } finally {
    loading.value = false
  }
}

const switchZone = (zoneKey) => {
  currentZone.value = zoneKey
  fetchRanking()
}

const switchStage = (stageKey) => {
  currentStage.value = stageKey
  fetchRanking()
}

const goBackCompetition = () => {
  router.push('/alliance/competition')
}

const goBackAlliance = () => {
  router.push('/alliance')
}

const goHome = () => {
  router.push('/')
}

const getZoneName = (key) => {
  const zone = zones.find(z => z.key === key)
  return zone ? zone.name : key
}

const getStageName = (key) => {
  const stage = stages.find(s => s.key === key)
  return stage ? stage.name : key
}

onMounted(() => {
  fetchRanking()
})
</script>

<template>
  <div class="ranking-page">
    <div v-if="loading">加载中...</div>
    <div v-else-if="errorMsg">{{ errorMsg }}</div>
    <template v-else-if="rankingData">
      <div>【战队排行】 第{{ rankingData.session || '2026-01-11' }}届</div>
      <div v-if="rankingData.honorText">{{ rankingData.honorText }}</div>
      <div>
        <template v-for="(zone, idx) in zones" :key="zone.key">
          <a class="link" @click="switchZone(zone.key)">{{ zone.name }}</a>
          <span v-if="idx < zones.length - 1">|</span>
        </template>
      </div>
      <div>
        (<a class="link" @click="switchStage('all')">全部</a>|
        <template v-for="(stage, idx) in stages" :key="stage.key">
          <a class="link" @click="switchStage(stage.key)">{{ stage.name }}</a>
          <span v-if="idx < stages.length - 1">|</span>
        </template>)
      </div>
      <div v-if="rankingData.rankings && rankingData.rankings.length > 0">
        <div v-for="(item, idx) in rankingData.rankings" :key="item.id || idx">
          {{ item.rank || (idx + 1) }}.『{{ item.alliance_name }}』第{{ item.rank || (idx + 1) }}名
        </div>
      </div>
      <div v-else>暂无排行数据</div>
      <div>
        <a class="link" @click="goBackCompetition">返回争霸赛</a>
      </div>
      <div>
        <a class="link" @click="goBackAlliance">返回联盟</a>
      </div>
      <div>
        <a class="link" @click="goHome">返回游戏首页</a>
      </div>
    </template>
  </div>
</template>

<style scoped>
.ranking-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 17px;
  line-height: 1.8;
  font-family: SimSun, "宋体", serif;
}

.link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}
</style>
