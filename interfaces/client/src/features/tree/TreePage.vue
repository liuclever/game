<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()

const loading = ref(true)
const errorMsg = ref('')
const msg = ref('')
const status = ref(null)

const isSunday = computed(() => Boolean(status.value?.is_sunday))
const canDrawToday = computed(() => Boolean(status.value?.can_draw_today))
const myNumbers = computed(() => status.value?.my_numbers || [])
const winningNumbers = computed(() => status.value?.winning_numbers || [])
const matchCount = computed(() => Number(status.value?.match_count || 0))
const star = computed(() => Number(status.value?.star || 0))
const claimed = computed(() => Boolean(status.value?.claimed))

const goRule = () => router.push('/tree/rule')
const goHome = () => router.push('/')
const goBack = () => router.back()

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
  msg.value = ''
  errorMsg.value = ''
  try {
    const res = await http.post('/tree/draw')
    if (res.data?.ok) {
      msg.value = `今日领取数字：${res.data.drawn_number}`
      await load()
    } else {
      errorMsg.value = res.data?.error || '领取失败'
    }
  } catch (e) {
    errorMsg.value = e?.response?.data?.error || '领取失败'
  }
}

const claim = async () => {
  msg.value = ''
  errorMsg.value = ''
  try {
    const res = await http.post('/tree/claim')
    if (res.data?.ok) {
      const c = res.data?.reward?.copper || 0
      const pill = res.data?.reward?.rebirth_pill || 0
      msg.value = pill > 0 ? `领取成功：铜钱+${c}，重生丹×${pill}` : `领取成功：铜钱+${c}`
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
      <span class="title">古树</span>
      <a class="link" @click="goRule">规则</a>
    </div>

    <div class="section" v-if="loading">加载中...</div>
    <div class="section red" v-else-if="errorMsg">{{ errorMsg }}</div>

    <template v-else-if="status">
      <div class="section">本周已领取：{{ myNumbers.length }}/7</div>
      <div class="section">
        我的数字：
        <span v-if="myNumbers.length === 0" class="gray">暂无</span>
        <span v-else class="nums">{{ myNumbers.join('，') }}</span>
      </div>

      <div class="section spacer">
        <a v-if="canDrawToday" class="link" @click="drawToday">领取今日数字</a>
        <span v-else class="gray">今日已领取或本周已满</span>
      </div>

      <div class="section" v-if="isSunday">
        中奖数字：
        <span v-if="winningNumbers.length === 0" class="gray">未开奖</span>
        <span v-else class="nums">{{ winningNumbers.join('，') }}</span>
      </div>
      <div class="section" v-if="isSunday && winningNumbers.length">
        命中：<span class="bold">{{ matchCount }}</span> 个
        <span class="gray">（{{ star }}星）</span>
      </div>

      <div class="section spacer" v-if="isSunday && winningNumbers.length">
        <a v-if="!claimed && star > 0" class="link red" @click="claim">领取本周礼包</a>
        <span v-else-if="claimed" class="gray">本周已领奖</span>
        <span v-else class="gray">未中奖</span>
      </div>

      <div class="section red" v-if="msg">{{ msg }}</div>

      <div class="section spacer">
        <a class="link" @click="goBack">返回前页</a>
      </div>
      <div class="section">
        <a class="link" @click="goHome">返回游戏首页</a>
      </div>
    </template>
  </div>
</template>

<style scoped>
.tree-page {
  background: #FFF8DC;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 13px;
  line-height: 1.7;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 2px 0;
}

.title-row {
  display: flex;
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


