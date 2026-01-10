<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const dungeonName = ref(route.params.name || '')
const floor = ref(1)
const beastName = ref('')
const beastLevel = ref(1)

const countsByItemId = ref({})
const message = ref('')
const obtainedBeast = ref(null)
const isLoading = ref(false)

const BALLS = [
  { itemId: 4002, name: '捕捉球', rate: 25 },
  { itemId: 4003, name: '强力捕捉球', rate: 45 },
]

const titleText = computed(() => {
  if (beastName.value) return `捕捉${beastName.value}`
  return '捕捉'
})

const getCount = (itemId) => {
  return Number(countsByItemId.value?.[String(itemId)] || 0)
}

const loadFromState = () => {
  const state = history.state || {}

  dungeonName.value = state.dungeonName || dungeonName.value
  floor.value = Number(state.floor || floor.value || 1)

  beastName.value = state.beastName || state.capturableBeast || ''
  beastLevel.value = Number(state.beastLevel || state.level || 1)

  // fallback: 从 sessionStorage 恢复
  if (!beastName.value) {
    const savedData = sessionStorage.getItem('currentDungeonBattle')
    if (savedData) {
      try {
        const parsed = JSON.parse(savedData)
        const bd = parsed?.battleData
        dungeonName.value = parsed?.dungeonName || dungeonName.value
        floor.value = Number(parsed?.floor || floor.value || 1)
        const firstBeast = bd?.beasts?.[0]
        if (firstBeast?.name) beastName.value = firstBeast.name
        if (firstBeast?.level) beastLevel.value = Number(firstBeast.level)
      } catch (e) {
        console.error('解析缓存战斗数据失败:', e)
      }
    }
  }
}

const fetchCounts = async () => {
  try {
    const res = await fetch('/api/dungeon/capture/info')
    const data = await res.json()
    if (data.ok) {
      countsByItemId.value = data.counts || {}
    } else {
      message.value = data.error || '获取捕捉球数量失败'
    }
  } catch (e) {
    console.error('获取捕捉球数量失败:', e)
    message.value = '网络错误'
  }
}

const useBall = async (ball) => {
  if (isLoading.value) return
  obtainedBeast.value = null
  message.value = ''

  if (!dungeonName.value || !beastName.value) {
    message.value = '缺少副本/幻兽信息，无法捕捉'
    return
  }

  if (getCount(ball.itemId) <= 0) {
    message.value = `${ball.name}不足`
    return
  }

  try {
    isLoading.value = true
    const res = await fetch('/api/dungeon/capture', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        dungeon_name: dungeonName.value,
        floor: floor.value,
        beast_name: beastName.value,
        level: beastLevel.value,
        ball_item_id: ball.itemId
      })
    })
    const data = await res.json()

    if (!data.ok) {
      message.value = data.error || '捕捉失败'
      return
    }

    message.value = data.message || (data.success ? '捕捉成功！' : '捕捉失败')
    if (data.counts) {
      countsByItemId.value = data.counts
    } else {
      await fetchCounts()
    }

    if (data.success && data.beast) {
      obtainedBeast.value = data.beast
    }
  } catch (e) {
    console.error('捕捉失败:', e)
    message.value = '网络错误'
  } finally {
    isLoading.value = false
  }
}

const goDungeon = () => {
  router.push(`/dungeon/challenge/${encodeURIComponent(dungeonName.value)}`)
}

const goHome = () => {
  router.push('/')
}

onMounted(async () => {
  loadFromState()
  await fetchCounts()
})
</script>

<template>
  <div class="capture-page">
    <div class="section title">{{ titleText }}</div>

    <div class="section" v-if="beastName">
      根据你战胜它的表现，似乎还没有完全【心服口服】，你可以消耗捕捉球来抓住它
    </div>

    <div v-if="message" class="section" :class="{ 'success': obtainedBeast, 'error': !obtainedBeast }">
      {{ message }}
    </div>

    <div class="section spacer"></div>

    <template v-if="obtainedBeast">
      <div class="section">
        你获得了幻兽【{{ obtainedBeast.name }}】！
      </div>
    </template>

    <template v-else>
      <div v-for="ball in BALLS" :key="ball.itemId" class="section">
        {{ ball.name }}×{{ getCount(ball.itemId) }}
        <a class="link" @click="useBall(ball)">使用</a>
        <span class="gray">（成功率{{ ball.rate }}%）</span>
      </div>
    </template>

    <div class="section spacer"></div>

    <div class="section">
      <a class="link" @click="goDungeon">返回副本</a>
    </div>

    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>

  </div>
</template>

<style scoped>
.capture-page {
  background: #FFF8DC;
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

.gray {
  color: #666666;
}

.small {
  font-size: 11px;
}

.success {
  color: #008800;
  font-weight: bold;
}

.error {
  color: #CC0000;
}

.footer {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #CCCCCC;
}
</style>
