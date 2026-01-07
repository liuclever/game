<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()

const loading = ref(true)
const errorMessage = ref('')
const matches = ref([])
const period = ref(0)
const currentType = ref(route.query.type || 'tiger') // tiger / crane
const meNickname = ref('')

const loadData = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    // 获取当前登录玩家昵称
    const meRes = await http.get('/auth/status')
    if (meRes.data && meRes.data.ok && meRes.data.nickname) {
      meNickname.value = meRes.data.nickname
    }

    const res = await http.get(`/battlefield/yesterday?type=${currentType.value}`)
    if (res.data.ok) {
      period.value = res.data.period || 0
      matches.value = res.data.matches || []
    } else {
      errorMessage.value = res.data.error || '加载战况失败'
    }
  } catch (e) {
    console.error('加载战况失败', e)
    errorMessage.value = '加载战况失败'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})

// 展示用的对战列表，按顺序排列
const displayMatches = computed(() => {
  // 只保留与当前玩家有关的战斗
  const filtered = matches.value.filter((m) => {
    if (!meNickname.value) return true // 若未获取到昵称，回退显示全部
    return m.firstPlayer === meNickname.value || m.secondPlayer === meNickname.value
  })

  return filtered.map((m, idx) => {
    const isFirstWin = !!m.isFirstWin
    const isFirst = meNickname.value && m.firstPlayer === meNickname.value
    const isSecond = meNickname.value && m.secondPlayer === meNickname.value
    // 以当前玩家视角判断胜负；若未获取到昵称则按前置玩家视角
    let win = isFirstWin
    if (meNickname.value) {
      if (isFirst) win = isFirstWin
      else if (isSecond) win = !isFirstWin
    }
    const resultLabel = win ? '胜' : '负'
    return {
      ...m,
      index: idx + 1,
      resultLabel: resultLabel,
      isWin: win,
    }
  })
})

const killCount = computed(() => displayMatches.value.filter(m => m.isWin).length)

const goBattle = (m) => {
  if (!m || !m.id) return
  router.push(`/battlefield/battle?id=${m.id}`)
}

const goBack = () => {
  router.back()
}

const goBattlefield = () => {
  router.push('/battlefield')
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="kill-page">
    <div class="section title">
      【杀敌详细】 <a class="link" @click="goBack">返回</a>
    </div>

    <div class="section gray">
      战场：{{ currentType === 'crane' ? '飞鹤战场' : '猛虎战场' }} 第{{ period || '—' }}期
    </div>

    <div v-if="loading" class="section">加载中...</div>
    <div v-else-if="errorMessage" class="section red">{{ errorMessage }}</div>

    <template v-else>
      <div class="section">
        杀敌：{{ killCount }}人
      </div>

      <div class="section" v-if="meNickname">
        当前玩家：{{ meNickname }}
      </div>

      <div class="section">
        顺序: 胜负, 名称
      </div>

      <div
        v-for="m in displayMatches"
        :key="m.id || m.index"
        class="section"
      >
        {{ m.index }}. {{ m.resultLabel }}.
        {{ m.firstPlayer }} VS {{ m.secondPlayer }}
        <a class="link" @click="goBattle(m)">查看</a>
      </div>

      <div v-if="!displayMatches.length" class="section gray">
        暂无对战记录
      </div>
    </template>

    <div class="nav">
      <a class="link" @click="goBattlefield">返回古战场</a>
      <span class="sep">|</span>
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>

  </div>
</template>

<style scoped>
.kill-page {
  background: #FFF8DC;
  min-height: 100vh;
  padding: 10px 12px;
  font-size: 14px;
  line-height: 1.8;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 4px 0;
}

.title {
  font-weight: bold;
}

.link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.red {
  color: #CC0000;
}

.gray {
  color: #666;
}

.nav {
  margin-top: 12px;
}

.sep {
  margin: 0 6px;
  color: #666;
}

.footer {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #CCCCCC;
}

.small {
  font-size: 11px;
}
</style>
