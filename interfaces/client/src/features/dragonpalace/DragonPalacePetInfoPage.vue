<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import http from '@/services/http'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const errorMsg = ref('')
const data = ref(null)

const type = computed(() => {
  const raw = route.query.type
  const n = parseInt(String(raw || '0'), 10)
  return Number.isFinite(n) ? n : 0
})

const load = async () => {
  loading.value = true
  errorMsg.value = ''
  try {
    const res = await http.get('/dragonpalace/petinfo', { params: { type: type.value } })
    if (res.data?.ok) {
      data.value = res.data
    } else {
      errorMsg.value = res.data?.error || '加载失败'
    }
  } catch (e) {
    errorMsg.value = e?.response?.data?.error || '网络错误'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  load()
})

const goBack = () => router.back()
const goHome = () => router.push('/')

const formatAtkLabel = (enemy) => {
  const t = String(enemy?.attack_type || '').toLowerCase()
  return t === 'magic' ? '法攻' : '物攻'
}
</script>

<template>
  <div class="petinfo-page">
    <div class="section">梦炽云召唤之星</div>

    <div v-if="loading" class="section">加载中...</div>
    <div v-else-if="errorMsg" class="section red">{{ errorMsg }}</div>

    <template v-else-if="data">
      <template v-for="(e, idx) in data.enemies" :key="idx">
        <div class="section title">{{ e.name }}</div>
        <div class="section indent">
          气血:{{ e.hp }} | {{ formatAtkLabel(e) }}:{{ e.atk }}
        </div>
        <div class="section indent">
          物防:{{ e.def }} | 法防:{{ e.mdef }}
        </div>
        <div class="section indent">
          速度:{{ e.speed }} | 综合战力:{{ e.power }}
        </div>
        <div class="section indent">
          技能:{{ (e.skills || []).join('｜') }}
        </div>
        <div class="section spacer" v-if="idx < data.enemies.length - 1"></div>
      </template>

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
.petinfo-page {
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
  margin-top: 8px;
}

.indent {
  padding-left: 16px;
}

.spacer {
  margin-top: 16px;
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
</style>


