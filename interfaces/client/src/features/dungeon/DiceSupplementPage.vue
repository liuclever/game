<script setup>
import { useMessage } from '@/composables/useMessage'
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const { message, messageType, showMessage } = useMessage()

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
      showMessage('使用成功，获得10个骰子', 'success')
    } else {
      showMessage(data.error || '使用失败', 'error')
    }
  } catch (e) {
    console.error('使用骰子包失败:', e)
    showMessage('网络错误', 'error')
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
    <!-- 消息提示 -->
    <div v-if="message" class="message" :class="messageType">
      {{ message }}
    </div>

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
  font-size: 13px;
}

.footer {
  margin-top: 40px;
  padding-top: 10px;
  border-top: 1px solid #EEEEEE;
  background: #F0F0F0;
  padding: 10px;
}

/* 消息提示样式 */
.message {
  padding: 12px;
  margin: 12px 0;
  border-radius: 4px;
  font-weight: bold;
  text-align: center;
}

.message.success {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.message.error {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.message.info {
  background: #d1ecf1;
  color: #0c5460;
  border: 1px solid #bee5eb;
}

</style>
