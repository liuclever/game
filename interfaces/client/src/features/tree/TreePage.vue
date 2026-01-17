<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()

const loading = ref(true)
const errorMsg = ref('')
const status = ref(null)

const canDrawToday = computed(() => Boolean(status.value?.can_draw_today))
const weekNo = computed(() => Number(status.value?.week_no || 0))
const todayNumber = computed(() => status.value?.today_number)
const redNumbers = computed(() => status.value?.red_numbers || [])
const blueNumber = computed(() => status.value?.blue_number)
const announceDate = computed(() => String(status.value?.announce_date || '').trim())

const lastWeek = computed(() => status.value?.last_week || null)
const lastRed = computed(() => lastWeek.value?.red_numbers || [])
const lastBlue = computed(() => lastWeek.value?.blue_number)
const lastWinningRed = computed(() => lastWeek.value?.winning_red_numbers || [])
const lastWinningBlue = computed(() => lastWeek.value?.winning_blue_number)
const lastStar = computed(() => Number(lastWeek.value?.star || 0))
const lastClaimed = computed(() => Boolean(lastWeek.value?.claimed))

const goRule = () => router.push('/tree/rule')
const goHome = () => router.push('/')

const load = async () => {
  loading.value = true
  errorMsg.value = ''
  try {
    const res = await http.get('/tree/status')
    if (res.data?.ok) {
      status.value = res.data
    } else {
      errorMsg.value = res.data?.error || '加载失败'
    }
  } catch (e) {
    errorMsg.value = e?.response?.data?.error || '加载失败'
  } finally {
    loading.value = false
  }
}

const drawToday = async () => {
  errorMsg.value = ''
  try {
    const res = await http.post('/tree/draw')
    if (res.data?.ok) {
      await load()
    } else {
      errorMsg.value = res.data?.error || '领取失败'
    }
  } catch (e) {
    errorMsg.value = e?.response?.data?.error || '领取失败'
  }
}

const claim = async () => {
  errorMsg.value = ''
  try {
    const res = await http.post('/tree/claim')
    if (res.data?.ok) {
      await load()
    } else {
      errorMsg.value = res.data?.error || '领奖失败'
    }
  } catch (e) {
    errorMsg.value = e?.response?.data?.error || '领奖失败'
  }
}

onMounted(() => load())
</script>

<template>
  <div class="tree-page">
    <div class="section title-row">
      <span class="title">【幸运古树】</span>
      <a class="link" @click="goRule">规则</a>
    </div>

    <div class="section" v-if="loading">加载中...</div>
    <div class="section red" v-else-if="errorMsg">{{ errorMsg }}</div>

    <template v-else-if="status">
      <div class="section gray">积累幸运数字,周周有望拿大奖</div>
      <div class="section">第{{ weekNo }}周</div>
      <div class="section">今日幸运数字: <span class="bold">{{ todayNumber ?? '暂无' }}</span></div>

      <div class="section spacer">我的本周幸运数字</div>
      <div class="section">红果实:<span class="nums">{{ redNumbers.length ? redNumbers.join(' ') : ' 暂无' }}</span></div>
      <div class="section">蓝果实:<span class="nums">{{ blueNumber != null ? ` ${blueNumber}` : ' 暂无' }}</span></div>

      <div class="section spacer">
        <a v-if="canDrawToday" class="link" @click="drawToday">领取</a>
        <span v-else class="gray">今日已领取</span>
      </div>

      <div class="section spacer">幸运数字公布时间</div>
      <div class="section">{{ announceDate }}</div>

      <template v-if="lastWeek">
        <div class="section spacer">我的上周数字</div>
        <div class="section">红果实:<span class="nums">{{ lastRed.length ? lastRed.join(' ') : ' 暂无' }}</span></div>
        <div class="section">蓝果实:<span class="nums">{{ lastBlue != null ? ` ${lastBlue}` : ' 暂无' }}</span></div>

        <div class="section spacer">上周幸运数字</div>
        <div class="section">红果实:<span class="nums">{{ lastWinningRed.length ? lastWinningRed.join(' ') : ' 暂无' }}</span></div>
        <div class="section">蓝果实:<span class="nums">{{ lastWinningBlue != null ? ` ${lastWinningBlue}` : ' 暂无' }}</span></div>

        <div class="section spacer" v-if="lastStar > 0">
          <span>您的幸运数字获得</span><span class="bold">{{ lastStar }}</span><span>星幸运礼包</span>
          <template v-if="!lastClaimed">
            <a class="link red" style="margin-left: 8px;" @click="claim">领取</a>
          </template>
          <template v-else>
            <span class="gray" style="margin-left: 8px;">已领取</span>
          </template>
        </div>
      </template>

      <div class="section spacer">
        <a class="link" @click="goHome">返回游戏首页</a>
      </div>
    </template>
  </div>
</template>

<style scoped>
.tree-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 12px 16px;
  font-size: 18px;
  line-height: 1.8;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 2px 0;
}

.title-row {
  align-items: baseline;
  justify-content: space-between;
  margin-top: 6px;
}

.title {
  font-weight: bold;
}

.nums {
  color: #333;
}

.bold {
  font-weight: bold;
  color: #cc0000;
}

.spacer {
  margin-top: 10px;
}

.link {
  color: #0033cc;
  cursor: pointer;
  margin-left: 6px;
}

.red {
  color: #cc3300;
}

.gray {
  color: #666;
}
</style>


