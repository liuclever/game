<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()

const currentType = ref(route.query.type || 'tiger')
const period = ref(0)
const matches = ref([])
const selectedRound = ref(1)
const loading = ref(true)
const errorMessage = ref('')

const loadYesterday = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const res = await http.get(`/battlefield/yesterday?type=${currentType.value}`)
    if (res.data.ok) {
      period.value = res.data.period || 0
      matches.value = res.data.matches || []
      // 默认选中第一轮
      if (matches.value.length > 0) {
        selectedRound.value = matches.value[0].round || 1
      }
    } else {
      errorMessage.value = res.data.error || '加载昨日战况失败'
    }
  } catch (e) {
    console.error('加载昨日战况失败', e)
    errorMessage.value = '加载昨日战况失败'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadYesterday()
})

const rounds = computed(() => {
  const set = new Set()
  for (const m of matches.value) {
    if (m.round) set.add(m.round)
  }
  const arr = Array.from(set)
  arr.sort((a, b) => a - b)
  // 如果没有数据，默认给 1-5 轮，方便前端展示空列表
  return arr.length ? arr : [1, 2, 3, 4, 5]
})

const currentRoundMatches = computed(() => {
  const r = selectedRound.value
  const list = matches.value.filter(m => m.round === r)
  // 按 match 字段排序
  list.sort((a, b) => (a.match || 0) - (b.match || 0))
  return list
})

const switchRound = (round) => {
  selectedRound.value = round
}

const watchBattle = (m) => {
  if (!m || !m.id) return
  router.push(`/battlefield/battle?id=${m.id}`)
}

const goBack = () => {
  router.push('/battlefield')
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="yesterday-page">
    <div class="section title">
      【昨日战况】 第{{ period || '—' }}期
    </div>

    <!-- 轮次切换 -->
    <div class="section rounds">
      <span
        v-for="r in rounds"
        :key="r"
        class="round-tab"
      >
        <a
          class="link"
          :class="{ active: selectedRound === r }"
          @click="switchRound(r)"
        >
          第{{ r }}轮
        </a>
      </span>
    </div>

    <div v-if="loading" class="section">加载中...</div>
    <div v-else-if="errorMessage" class="section red">{{ errorMessage }}</div>

    <!-- 对战列表 -->
    <template v-else>
      <div
        v-for="(m, index) in currentRoundMatches"
        :key="m.id || index"
        class="section"
      >
        {{ index + 1 }}.
        {{ m.firstPlayer }}
        <template v-if="m.resultLabel">
          ({{ m.resultLabel }})
        </template>
        VS {{ m.secondPlayer }}
        <a class="link" @click="watchBattle(m)">观战</a>
      </div>

      <div v-if="!currentRoundMatches.length" class="section gray">
        暂无对战记录
      </div>
    </template>

    <!-- 返回链接 -->
    <div class="section spacer">
      <a class="link" @click="goBack">返回战场</a>
    </div>
    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>

  </div>
</template>

<style scoped>
.yesterday-page {
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

.rounds {
  margin-top: 4px;
}

.round-tab {
  margin-right: 6px;
}

.link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.link.active {
  font-weight: bold;
}

.gray {
  color: #666;
}

.red {
  color: #CC0000;
}

.spacer {
  margin-top: 16px;
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
