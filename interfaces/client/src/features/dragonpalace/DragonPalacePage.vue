<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()

const loading = ref(false)
const errorMsg = ref('')
const msg = ref('')

const status = ref(null)

const loadStatus = async () => {
  loading.value = true
  errorMsg.value = ''
  try {
    const res = await http.get('/dragonpalace/status')
    if (res.data?.ok) {
      status.value = res.data
    } else {
      errorMsg.value = res.data?.error || '加载失败'
    }
  } catch (e) {
    errorMsg.value = e?.response?.data?.error || '网络错误'
  } finally {
    loading.value = false
  }
}

const goIntro = () => {
  router.push('/dragonpalace/intro')
}

const goHome = () => {
  router.push('/')
}

const doReset = async () => {
  msg.value = ''
  try {
    const res = await http.post('/dragonpalace/reset')
    if (res.data?.ok) {
      msg.value = res.data?.message || '重置成功'
      await loadStatus()
    } else {
      alert(res.data?.error || '重置失败')
    }
  } catch (e) {
    alert(e?.response?.data?.error || '重置失败')
  }
}

const doChallenge = async () => {
  msg.value = ''
  try {
    const res = await http.post('/dragonpalace/challenge')
    if (res.data?.ok) {
      // 存入 sessionStorage，供“详细战报”页刷新恢复
      sessionStorage.setItem('currentDragonPalaceBattle', JSON.stringify({
        battleData: res.data.battle_data,
        stage: status.value?.current_stage || 1
      }))
      msg.value = res.data?.message || '挑战完成'
      await loadStatus()
    } else {
      alert(res.data?.error || '挑战失败')
    }
  } catch (e) {
    alert(e?.response?.data?.error || '挑战失败')
  }
}

const viewReport = async (stage) => {
  msg.value = ''
  try {
    const res = await http.get('/dragonpalace/report', { params: { stage } })
    if (res.data?.ok) {
      const battleData = {
        battles: res.data.report?.battles || []
      }
      sessionStorage.setItem('currentDragonPalaceBattle', JSON.stringify({ battleData, stage }))
      router.push({
        path: '/dragonpalace/detail-report',
        query: { stage, index: 0 },
        state: { battleData, stage }
      })
    } else {
      alert(res.data?.error || '暂无战报')
    }
  } catch (e) {
    alert(e?.response?.data?.error || '暂无战报')
  }
}

const claimReward = async (stage) => {
  msg.value = ''
  try {
    const res = await http.post('/dragonpalace/claim', { stage })
    if (res.data?.ok) {
      // 领取后跳转到“领取成功”页（文案与外站一致）
      sessionStorage.setItem('dragonpalaceLastClaimMsg', res.data?.message || '领取成功，获得龙宫之谜探索礼包')
      await loadStatus()
      router.push('/dragonpalace/reward')
    } else {
      alert(res.data?.error || '领取失败')
    }
  } catch (e) {
    alert(e?.response?.data?.error || '领取失败')
  }
}

const goPetInfo = (stage) => {
  router.push({ path: '/dragonpalace/petinfo', query: { type: stage } })
}

onMounted(() => {
  loadStatus()
})
</script>

<template>
  <div class="dragonpalace-page">
    <div class="section title">
      【龙宫之谜】<a class="link" @click="goIntro">活动简介</a>
    </div>

    <div class="section">活动时间:{{ status?.open_time_text || '10:00-24:00' }}</div>
    <div class="section">今日挑战:{{ status?.today_used ?? 0 }}/{{ status?.today_free ?? 1 }}</div>
    <div class="section">
      重置次数:{{ status?.resets_used ?? 0 }}/{{ status?.max_resets ?? 2 }}.
      <a class="link" @click="doReset">重置({{ status?.reset_cost_yuanbao ?? 200 }}元宝)</a>
    </div>

    <div class="section" v-if="loading">加载中...</div>
    <div class="section red" v-else-if="errorMsg">{{ errorMsg }}</div>

    <template v-else-if="status">
      <div
        v-for="s in status.stages"
        :key="s.stage"
        class="section"
      >
        关卡{{ s.stage }}（推荐{{ s.recommend_level }}级）:
        <a class="link" @click="goPetInfo(s.stage)">{{ s.name }}</a>
        <a
          v-if="status.open && status.status !== 'failed' && status.status !== 'completed' && status.current_stage === s.stage"
          class="link"
          @click="doChallenge"
        >挑战</a>
      </div>

      <div class="section red" v-if="msg">{{ msg }}</div>

      <div class="section spacer">战斗历史:</div>
      <div
        v-for="h in status.history"
        :key="h.stage"
        class="section"
      >
        <template v-if="h.success">
          第{{ h.stage }}关挑战成功
          <a class="link" @click="viewReport(h.stage)">查看战报</a>
          <a v-if="h.can_claim" class="link" @click="claimReward(h.stage)">领取奖励</a>
          <span v-else class="gray">（已领取）</span>
        </template>
      </div>

      <div class="section spacer">
        <a class="link" @click="goHome">返回游戏首页</a>
      </div>
    </template>
  </div>
</template>

<style scoped>
.dragonpalace-page {
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
  margin-bottom: 6px;
}

.spacer {
  margin-top: 16px;
}

.link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: none;
  margin-left: 6px;
}

.link:hover {
  text-decoration: underline;
}

.gray {
  color: #666666;
}

.red {
  color: #CC0000;
}
</style>


