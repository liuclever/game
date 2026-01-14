<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()

const loading = ref(false)
const signupLoading = ref(false)
const checkinLoading = ref(false)
const errorMessage = ref('')
const defaultStatistics = {
  dragon_count: 0,
  tiger_count: 0,
  total_signed: 0,
  threshold_level: 40,
}

const warInfo = ref({
  seasonText: '第2025-12-24届',
  countdownText: '倒计时',
  personal: null,
  statistics: { ...defaultStatistics },
  schedule: null,
  targets: {
    dragon_registration: null,
    tiger_registration: null,
  },
})
const scheduleInfo = ref(null)
const countdownSeconds = ref(0)
let countdownTimer = null

const fetchWarInfo = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const res = await http.get('/alliance/war/info')
    if (res.data?.ok && res.data.data) {
      const data = res.data.data
      warInfo.value = {
        ...warInfo.value,
        personal: data.personal || null,
        statistics: { ...defaultStatistics, ...(data.statistics || {}) },
        armies: data.armies || { dragon: [], tiger: [] },
        schedule: data.schedule || null,
        targets: data.targets || {
          dragon_registration: null,
          tiger_registration: null,
        },
      }
      scheduleInfo.value = data.schedule || null
      if (scheduleInfo.value && typeof scheduleInfo.value.countdownSeconds === 'number') {
        startCountdown(scheduleInfo.value.countdownSeconds)
      } else {
        clearCountdown()
      }
    } else if (res.data?.error) {
      errorMessage.value = res.data.error
    }
  } catch (err) {
    console.error('加载盟战信息失败', err)
    errorMessage.value = '加载盟战信息失败'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchWarInfo()
})

const goAlliance = () => {
  router.push('/alliance')
}

const goHome = () => {
  router.push('/')
}

const goToDragonSignup = () => {
  router.push('/alliance/war/dragon-signup')
}

const handleQuickLink = (type) => {
  if (type === 'rule') {
    router.push('/alliance/war/rules')
    return
  }
  if (type === 'honor-shop') {
    router.push('/alliance/war/honor')
    return
  }
  if (type === 'ranking') {
    router.push('/alliance/war/ranking')
    return
  }
  if (type === 'targets') {
    router.push('/alliance/war/targets')
    return
  }
  if (type === 'live') {
    router.push('/alliance/war/live')
    return
  }
  if (type === 'camp') {
    router.push('/alliance/barracks')
    return
  }
  if (type === 'record') {
    router.push('/alliance/war/battle-records')
    return
  }
  console.log(`Alliance war quick link clicked: ${type}`)
}

const signupDisabled = computed(() => signupLoading.value || !!warInfo.value.personal?.signed_up)

const handleSignup = async () => {
  if (signupDisabled.value) {
    return
  }
  signupLoading.value = true
  try {
    const res = await http.post('/alliance/war/signup')
    if (res.data?.ok && res.data.data) {
      // 跳转到报名成功页面
      router.push({
        path: '/alliance/war/signup-success',
        query: {
          army_label: res.data.data.army_label
        }
      })
    } else {
      alert(res.data?.error || '报名失败')
    }
  } catch (err) {
    console.error('联盟报名失败', err)
    alert(err.response?.data?.error || '报名失败')
  } finally {
    signupLoading.value = false
  }
}

const handleCheckin = async () => {
  if (checkinLoading.value) {
    return
  }
  checkinLoading.value = true
  try {
    const res = await http.post('/alliance/war/checkin')
    if (res.data?.ok) {
      router.push({
        path: '/alliance/war/checkin-result',
        query: {
          success: 'true',
          message: res.data.message || '签到成功，获得30000铜钱'
        }
      })
    } else {
      router.push({
        path: '/alliance/war/checkin-result',
        query: {
          success: 'false',
          message: res.data?.error || '签到失败'
        }
      })
    }
  } catch (err) {
    console.error('盟战签到失败', err)
    router.push({
      path: '/alliance/war/checkin-result',
      query: {
        success: 'false',
        message: err.response?.data?.error || '签到失败'
      }
    })
  } finally {
    checkinLoading.value = false
  }
}

const startCountdown = (seconds) => {
  clearCountdown()
  countdownSeconds.value = Math.max(0, seconds)
  if (countdownSeconds.value <= 0) {
    return
  }
  countdownTimer = setInterval(() => {
    if (countdownSeconds.value <= 1) {
      countdownSeconds.value = 0
      clearCountdown()
    } else {
      countdownSeconds.value -= 1
    }
  }, 1000)
}

const clearCountdown = () => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }
}

onUnmounted(() => {
  clearCountdown()
})

const weekdayLabels = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
const pad = (value) => value.toString().padStart(2, '0')

const nextWarDisplay = computed(() => {
  if (!scheduleInfo.value?.nextWarTime) {
    return '待定'
  }
  const date = new Date(scheduleInfo.value.nextWarTime)
  if (Number.isNaN(date.getTime())) {
    return scheduleInfo.value.nextWarTime
  }
  return `${weekdayLabels[date.getDay()]} ${pad(date.getHours())}:${pad(date.getMinutes())}`
})

const scheduleDetailText = computed(() => {
  if (!scheduleInfo.value?.weekdaysDetail?.length) {
    return ''
  }
  return scheduleInfo.value.weekdaysDetail
    .map((item) => `${item.label}${pad(item.hour)}:${pad(item.minute || 0)}`)
    .join(' / ')
})

const countdownDisplay = computed(() => {
  return formatCountdown(countdownSeconds.value)
})

const formatCountdown = (seconds) => {
  if (seconds <= 0) {
    return '即将开战'
  }
  const hrs = Math.floor(seconds / 3600)
  const mins = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60
  const parts = []
  if (hrs > 0) {
    parts.push(`${hrs}小时`)
  }
  if (mins > 0 || hrs > 0) {
    parts.push(`${mins}分`)
  }
  parts.push(`${secs}秒`)
  return parts.join('')
}
</script>

<template>
  <div class="war-page">
    <div class="section title-row">
      【召唤盟战】<a class="link" @click.prevent="handleQuickLink('rule')">规则</a>
    </div>
    <div class="section intro">
      天下纷争，召唤大陆风云再起
    </div>

    <div class="section nav-links">
      <a class="link" @click.prevent="handleQuickLink('honor-shop')">战功兑换</a>
      ·
      <a class="link" @click.prevent="handleQuickLink('ranking')">盟战排行榜</a>
      ·
      <a class="link" @click.prevent="handleQuickLink('live')">盟战直播</a>
      ·
      <a class="link" @click.prevent="handleQuickLink('camp')">联盟兵营</a>
    </div>

    <div v-if="loading" class="section">加载中...</div>
    <div v-else-if="errorMessage" class="section red">{{ errorMessage }}</div>

    <template v-else>
      <div class="section-group">
        <div class="group-title">
          联盟备战
          <span class="divider">|</span>
          <a class="link" @click.prevent="handleQuickLink('record')">联盟战绩</a>
        </div>
        <div class="group-content">
          <div class="schedule-row" v-if="scheduleInfo">
            下一次开战：
            <span class="blue">{{ nextWarDisplay }}</span>
            <span class="gray">
              （倒计时：{{ countdownDisplay }}）
            </span>
          </div>
          <div v-else class="schedule-row">
            下一次开战：<span class="blue">待定</span>
          </div>
          <div v-if="scheduleDetailText" class="schedule-row">
            固定开战日：<span class="blue">{{ scheduleDetailText }}</span>
          </div>
          <div>
            查看全部攻城目标：<a class="link" @click.prevent="handleQuickLink('targets')">查看</a>
          </div>
          <div>{{ warInfo.seasonText }}</div>
          <div>
            盟战时间：<span class="blue">{{ warInfo.countdownText }}</span>
          </div>
          <div>
            飞龙军报名：
            <span class="orange">
              {{ warInfo.personal?.current_army === 1 ? '已报名' : '未报名' }}
            </span>
            <a
              v-if="warInfo.personal?.current_army !== 1"
              class="link"
              @click.prevent="goToDragonSignup"
            >报名</a>
          </div>
          <div>
            伏虎军报名：
            <span class="orange">
              {{ warInfo.personal?.current_army === 2 ? '已报名' : '未报名' }}
            </span>
          </div>
          <div>
            个人签到：
            <span class="orange">
              <template v-if="warInfo.personal?.signed_up">
                {{ warInfo.personal.current_army_label }}（{{ warInfo.personal?.checked_in ? '已签到' : '未签到' }}）
              </template>
              <template v-else>
                未报名
              </template>
            </span>
            <a
              v-if="!warInfo.personal?.signed_up"
              class="link"
              :class="{ disabled: signupDisabled }"
              @click.prevent="handleSignup"
            >{{ signupLoading ? '报名中...' : '报名' }}</a>
            <a
              v-else-if="warInfo.personal?.signed_up && !warInfo.personal?.checked_in"
              class="link"
              :class="{ disabled: checkinLoading }"
              @click.prevent="handleCheckin"
            >{{ checkinLoading ? '签到中...' : '签到' }}</a>
          </div>
          <div>
            飞龙军签到人数：<span class="blue">{{ warInfo.statistics?.dragon_count ?? 0 }}</span>
          </div>
          <div>
            伏虎军签到人数：<span class="blue">{{ warInfo.statistics?.tiger_count ?? 0 }}</span>
          </div>
          <div>
            已报名总人数：<span class="blue">{{ warInfo.statistics?.total_signed ?? 0 }}</span>
          </div>
        </div>
      </div>

      <div class="section-group">
        <div class="group-title">【攻城目标】</div>
        <div class="group-content">
          <template v-if="warInfo.targets?.dragon_registration || warInfo.targets?.tiger_registration">
            <div v-if="warInfo.targets.dragon_registration">
              飞龙军目标：<span class="blue">{{ warInfo.targets.dragon_registration.land_name }}</span>
            </div>
            <div v-if="warInfo.targets.tiger_registration">
              伏虎军目标：<span class="blue">{{ warInfo.targets.tiger_registration.land_name }}</span>
            </div>
          </template>
          <template v-else>
            盟主暂未选择
          </template>
        </div>
      </div>
    </template>

    <div class="section spacer">
      <a class="link" @click.prevent="goAlliance">返回联盟</a>
    </div>
    <div class="section">
      <a class="link" @click.prevent="goHome">返回游戏首页</a>
    </div>

  </div>
</template>

<style scoped>
.war-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 12px 16px 20px;
  font-size: 16px;
  line-height: 1.5;
  font-family: 'SimSun', '宋体', serif;
  color: #000;
}

.section {
  margin: 4px 0;
}

.schedule-row {
  margin: 2px 0;
}

.title-row {
  font-weight: bold;
  font-size: 18px;
}

.intro {
  color: #000;
}

.nav-links {
  font-size: 18px;
}

.link {
  color: #0066cc;
  cursor: pointer;
}

.link:hover {
  text-decoration: underline;
}

.section-group {
  margin-top: 10px;
  padding: 0;
  border: none;
  background: transparent;
  border-radius: 0;
  box-shadow: none;
}

.group-title {
  font-weight: bold;
  margin-bottom: 4px;
}

.group-content {
  padding-left: 0;
}

.divider {
  color: #666;
  margin: 0 6px;
}

.blue {
  color: #0066cc;
}

.orange {
  color: #cc6600;
}

.red {
  color: #cc0000;
}

.gray {
  color: #777;
}

.small {
  font-size: 17px;
}

.footer {
  margin-top: 16px;
}

.spacer {
  margin-top: 12px;
}
</style>
