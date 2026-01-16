<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const dungeonName = ref(decodeURIComponent(route.params.name || ''))
const mizongCount = ref(0)
const currentFloor = ref(1)
const totalFloors = ref(35)
const floorStatus = ref(['怪', '怪', '精', '怪', 'boss'])
const isLoading = ref(false)
const resultMessage = ref('')

const fetchMizongInfo = async () => {
  try {
    const res = await fetch('/api/dungeon/mizong/info')
    const data = await res.json()
    if (data.ok) {
      mizongCount.value = data.count
    }
  } catch (e) {
    console.error('获取迷踪符数量失败:', e)
  }
}

const fetchDungeonProgress = async () => {
  try {
    const res = await fetch(`/api/dungeon/progress?dungeon_name=${encodeURIComponent(dungeonName.value)}`)
    const data = await res.json()
    if (data.ok) {
      currentFloor.value = data.current_floor
      totalFloors.value = data.total_floors
    }
  } catch (e) {
    console.error('获取副本进度失败:', e)
  }
}

const useMizong = async (steps) => {
  if (mizongCount.value <= 0) {
    resultMessage.value = '迷踪符不足'
    return
  }
  
  isLoading.value = true
  resultMessage.value = ''
  
  try {
    const res = await fetch('/api/dungeon/mizong/use', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        dungeon_name: dungeonName.value,
        steps: steps
      })
    })
    const data = await res.json()
    if (data.ok) {
      resultMessage.value = `使用迷踪符成功！从第${data.old_floor}层前进到第${data.new_floor}层`
      if (data.is_reset) {
        resultMessage.value = `恭喜通关！从第${data.old_floor}层通关，层数重置为第1层`
      }
      mizongCount.value = data.remaining_count
      currentFloor.value = data.new_floor
    } else {
      resultMessage.value = data.error || '使用失败'
    }
  } catch (e) {
    console.error('使用迷踪符失败:', e)
    resultMessage.value = '网络错误'
  } finally {
    isLoading.value = false
  }
}

const goBack = () => {
  router.push(`/dungeon/challenge/${encodeURIComponent(dungeonName.value)}`)
}

const goMap = () => {
  router.push('/map')
}

const goHome = () => {
  router.push('/')
}

onMounted(() => {
  fetchMizongInfo()
  fetchDungeonProgress()
})
</script>

<template>
  <div class="mizong-page">
    <div class="section title">
      【迷踪跃步】 迷踪符 × {{ mizongCount }}
    </div>

    <div class="section">
      简介: 消耗1张迷踪符，即可将骰子前进结果指定为任意1-6的数字
    </div>

    <div class="section">
      当前: {{ dungeonName }} ({{ currentFloor }}/{{ totalFloors }}层)
    </div>

    <div class="section spacer"></div>

    <div class="section">
      <a class="link" :class="{ disabled: isLoading || mizongCount <= 0 }" @click="useMizong(1)">前进1层</a> | 
      <a class="link" :class="{ disabled: isLoading || mizongCount <= 0 }" @click="useMizong(2)">前进2层</a>
    </div>
    <div class="section">
      <a class="link" :class="{ disabled: isLoading || mizongCount <= 0 }" @click="useMizong(3)">前进3层</a> | 
      <a class="link" :class="{ disabled: isLoading || mizongCount <= 0 }" @click="useMizong(4)">前进4层</a>
    </div>
    <div class="section">
      <a class="link" :class="{ disabled: isLoading || mizongCount <= 0 }" @click="useMizong(5)">前进5层</a> | 
      <a class="link" :class="{ disabled: isLoading || mizongCount <= 0 }" @click="useMizong(6)">前进6层</a>
    </div>

    <div v-if="resultMessage" class="section result" :class="{ error: resultMessage.includes('不足') || resultMessage.includes('失败') }">
      {{ resultMessage }}
    </div>

    <div class="section spacer"></div>

    <div class="section">
      <a class="link" @click="goBack">返回副本</a>
    </div>
    <div class="section">
      <a class="link" @click="goMap">返回地图首页</a>
    </div>
    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>

  </div>
</template>

<style scoped>
.mizong-page {
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
  font-weight: bold;
}

.spacer {
  height: 12px;
}

.link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.link.disabled {
  color: #999;
  cursor: not-allowed;
}

.link.disabled:hover {
  text-decoration: none;
}

.gray {
  color: #666666;
}

.small {
  font-size: 17px;
}

.footer {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #CCCCCC;
}

.result {
  padding: 8px;
  background: #e8f5e9;
  border: 1px solid #a5d6a7;
  border-radius: 4px;
  color: #2e7d32;
}

.result.error {
  background: #ffebee;
  border-color: #ef9a9a;
  color: #c62828;
}

</style>
