<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()

const goToDailyTasks = () => {
  router.push('/tasks/daily')
}

const loading = ref(true)
const user = ref(null)
const errorMsg = ref('')
const rewardMsg = ref('')

const hasSignedToday = computed(() => {
  const last = String(user.value?.last_signin_date || '').trim()
  if (!last) return false
  const today = new Date()
  const yyyy = today.getFullYear()
  const mm = String(today.getMonth() + 1).padStart(2, '0')
  const dd = String(today.getDate()).padStart(2, '0')
  return last === `${yyyy}-${mm}-${dd}`
})

const load = async () => {
  loading.value = true
  errorMsg.value = ''
  try {
    const res = await http.get('/auth/status')
    if (res.data?.logged_in) {
      user.value = res.data
    } else {
      user.value = null
    }
  } catch (e) {
    console.error('加载登录状态失败', e)
    errorMsg.value = '加载失败'
  } finally {
    loading.value = false
  }
}

const doSignin = async () => {
  if (!user.value) return
  if (hasSignedToday.value) return
  rewardMsg.value = ''
  try {
    const res = await http.post('/player/signin')
    if (res.data?.ok) {
      const issuer = String(res.data?.issuer_name || '').trim()
      const copper = res.data?.reward?.copper || 0
      const multi = res.data?.reward?.multiplier || 1
      rewardMsg.value = issuer
        ? `已发放奖励：颁发者【${issuer}】，铜钱+${copper}${multi >= 2 ? ' (×2)' : ''}`
        : `已发放奖励：铜钱+${copper}${multi >= 2 ? ' (×2)' : ''}`
      await load()
    } else {
      rewardMsg.value = res.data?.error || '签到失败'
    }
  } catch (e) {
    rewardMsg.value = e?.response?.data?.error || '签到失败'
  }
}

onMounted(() => load())
</script>

<template>
  <div class="panel">
    <div>
      <template v-if="user">
        欢迎您，<span class="name">{{ user.nickname }}</span> (ID:{{ user.user_id }})
        <span class="link">好友 &gt;&gt;</span>
      </template>
      <template v-else>
        <span class="gray">未登录</span>
      </template>
    </div>
    <div class="mt">
      每日必做 <span class="strong">12/14</span> 项
      <span class="link" @click="goToDailyTasks">查看</span>
    </div>
    <div class="mt">
      今日
      <template v-if="loading">加载中...</template>
      <template v-else-if="errorMsg"><span class="red">{{ errorMsg }}</span></template>
      <template v-else-if="user">
        <span v-if="hasSignedToday">已签到</span>
        <span v-else class="link" @click="doSignin">签到</span>
      </template>
    </div>
    <div class="mt red" v-if="rewardMsg">{{ rewardMsg }}</div>
  </div>
</template>

<style scoped>
.panel {
  border: 1px solid #dddddd;
  padding: 6px 8px;
}

.mt {
  margin-top: 2px;
}

.name {
  color: #cc3300;
  font-weight: bold;
}

.link {
  color: #0033cc;
  cursor: pointer;
  margin-left: 4px;
}

.strong {
  color: #cc0000;
  font-weight: bold;
}

.gray {
  color: #666;
}

.red {
  color: #cc3300;
}
</style>
