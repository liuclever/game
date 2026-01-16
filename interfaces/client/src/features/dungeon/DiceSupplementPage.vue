<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const dice = ref(0)
const bagCount = ref(0)
const isLoading = ref(false)
const fromDungeon = ref(route.query.from || '')

const fetchDiceInfo = async () => {
  try {
    const res = await fetch('/api/dungeon/dice-info')
    const data = await res.json()
    if (data.ok) {
      dice.value = data.dice
      bagCount.value = data.bag_count
    }
  } catch (e) {
    console.error('获取骰子信息失败:', e)
  }
}

const useBag = async () => {
  if (bagCount.value <= 0 || isLoading.value) return
  
  try {
    isLoading.value = true
    const res = await fetch('/api/dungeon/dice/use-bag', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    })
    const data = await res.json()
    if (data.ok) {
      dice.value = data.dice
      bagCount.value = data.bag_count
      alert('使用成功，获得10个骰子')
    } else {
      alert(data.error || '使用失败')
    }
  } catch (e) {
    console.error('使用骰子包失败:', e)
    alert('网络错误')
  } finally {
    isLoading.value = false
  }
}

const goDungeon = () => {
  if (fromDungeon.value) {
    router.push(`/dungeon/challenge/${encodeURIComponent(fromDungeon.value)}`)
  } else {
    router.back()
  }
}

const goMap = () => {
  router.push('/map')
}

const goHome = () => {
  router.push('/')
}

onMounted(() => {
  fetchDiceInfo()
})
</script>

<template>
  <div class="dice-supplement-page">
    <div class="section title">
      现有骰子:{{ dice }}
    </div>

    <div class="section">
      骰子包×{{ bagCount }}. <a class="link" @click="useBag">使用</a>
    </div>

    <div class="section spacer"></div>

    <div class="section">
      <a class="link" @click="goDungeon">返回副本</a>
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
.dice-supplement-page {
  background: #fdfdfd;
  min-height: 100vh;
  padding: 15px;
  font-size: 16px;
  line-height: 1.8;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 10px 0;
}

.title {
  font-size: 20px;
  font-weight: bold;
}

.spacer {
  height: 30px;
}

.link {
  color: #0000EE;
  cursor: pointer;
  text-decoration: underline;
}

.gray {
  color: #666666;
}

.small {
  font-size: 16px;
}

.footer {
  margin-top: 40px;
  padding-top: 10px;
  border-top: 1px solid #EEEEEE;
  background: #ffffff;
  padding: 10px;
}
</style>
