<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const loading = ref(true)
const competitionInfo = ref(null)
const errorMsg = ref('')

const zones = [
  { name: '犊虎区', key: 'calf_tiger' },
  { name: '白虎区', key: 'white_tiger' },
  { name: '青龙区', key: 'azure_dragon' },
  { name: '朱雀区', key: 'vermillion_bird' },
  { name: '玄武区', key: 'black_tortoise' },
  { name: '战神区', key: 'god_of_war' },
]

const fetchCompetitionInfo = async () => {
  loading.value = true
  errorMsg.value = ''
  try {
    const res = await http.get('/alliance/competition')
    if (res.data?.ok) {
      competitionInfo.value = res.data
    } else {
      errorMsg.value = res.data?.error || '获取争霸赛信息失败'
    }
  } catch (err) {
    console.error('获取争霸赛信息失败', err)
    errorMsg.value = err.response?.data?.error || '网络错误，请稍后重试'
  } finally {
    loading.value = false
  }
}

const goBackAlliance = () => {
  router.push('/alliance')
}

const goHome = () => {
  router.push('/')
}

const goToTeamRanking = () => {
  router.push('/alliance/competition/team-ranking')
}

const goToEliteRanking = () => {
  router.push('/alliance/competition/elite-ranking')
}

const goToAllianceRanking = () => {
  router.push('/alliance/competition/alliance-ranking')
}

const goToPastRecords = () => {
  router.push('/alliance/competition/past-records')
}

const goToRules = () => {
  router.push('/alliance/competition/rules')
}

const registerZone = async (zoneKey) => {
  try {
    const res = await http.post('/alliance/competition/register', { team_keys: [zoneKey] })
    if (res.data.ok) {
      // 跳转到成功页面
      router.push({
        path: '/alliance/competition/signup-result',
        query: {
          success: 'true',
          message: res.data.message || '报名成功'
        }
      })
    } else {
      // 跳转到失败页面
      router.push({
        path: '/alliance/competition/signup-result',
        query: {
          success: 'false',
          error: res.data.error || '报名失败'
        }
      })
    }
  } catch (err) {
    // 跳转到失败页面
    router.push({
      path: '/alliance/competition/signup-result',
      query: {
        success: 'false',
        error: err.response?.data?.error || '报名失败，请稍后再试'
      }
    })
  }
}

const signup = async () => {
  try {
    const res = await http.post('/alliance/competition/signup')
    if (res.data.ok) {
      // 跳转到成功页面
      router.push({
        path: '/alliance/competition/signup-result',
        query: {
          success: 'true',
          message: res.data.message || '签到成功'
        }
      })
    } else {
      // 跳转到失败页面
      router.push({
        path: '/alliance/competition/signup-result',
        query: {
          success: 'false',
          error: res.data.error || '签到失败'
        }
      })
    }
  } catch (err) {
    // 跳转到失败页面
    router.push({
      path: '/alliance/competition/signup-result',
      query: {
        success: 'false',
        error: err.response?.data?.error || '签到失败，请稍后再试'
      }
    })
  }
}

onMounted(() => {
  fetchCompetitionInfo()
})
</script>

<template>
  <div class="competition-page">
    <div v-if="loading">加载中...</div>
    <div v-else-if="errorMsg">{{ errorMsg }}</div>
    <template v-else>
      <div>【联盟精英争霸赛】<a class="link" @click="goToRules">规则</a></div>
      <div>联盟精英云集,抢夺召唤大陆王者精英战队称号!</div>
      <div>
        <a class="link" @click="goToTeamRanking">战队排行</a>.
        <a class="link" @click="goToEliteRanking">精英排行</a>
      </div>
      <div>
        <a class="link" @click="goToAllianceRanking">联盟积分排行</a>.
        <a class="link" @click="goToPastRecords">往届战绩</a>
      </div>
      <div v-if="competitionInfo">
        第{{ competitionInfo.session || '2026-01-18' }}届 {{ competitionInfo.phase || '报名阶段' }}
      </div>
      <div v-else>
        第2026-01-18届 报名阶段
      </div>
      
      <div v-for="zone in zones" :key="zone.key">
        {{ zone.name }}争霸报名:
        <template v-if="competitionInfo?.zones?.[zone.key]?.registered">
          已报名
        </template>
        <template v-else>
          <a class="link" @click="registerZone(zone.key)">未报名</a>
        </template>
      </div>
      
      <div>
        个人签到:
        <template v-if="competitionInfo?.personalSignup?.registered">
          已报名
          <span v-if="competitionInfo?.personalSignup?.team">({{ competitionInfo.personalSignup.team }})</span>
        </template>
        <template v-else>
          <a class="link" @click="signup">未报名</a>
        </template>
      </div>
      <div>(成员签到1人方可激活)</div>
      
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
.competition-page {
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
