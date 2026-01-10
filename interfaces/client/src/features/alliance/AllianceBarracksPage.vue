<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()

const loading = ref(true)
const errorMessage = ref('')
const dragonArmy = ref([])
const tigerArmy = ref([])

const fetchBarracks = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const res = await http.get('/alliance/barracks')
    if (res.data?.ok && res.data.data) {
      const data = res.data.data
      dragonArmy.value = data.dragon || []
      tigerArmy.value = data.tiger || []
    } else {
      errorMessage.value = res.data?.error || '加载联盟兵营失败'
    }
  } catch (err) {
    console.error('加载联盟兵营失败', err)
    errorMessage.value = err.response?.data?.error || '加载联盟兵营失败'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchBarracks()
})

const goWar = () => router.push('/alliance/war')
const goAlliance = () => router.push('/alliance')
const goHome = () => router.push('/')
</script>

<template>
  <div class="barracks-page">
    <div class="section title-row">
      【联盟兵营】 <a class="link" @click.prevent="goWar">返回</a>
    </div>

    <div v-if="loading" class="section">加载中...</div>
    <div v-else-if="errorMessage" class="section red">{{ errorMessage }}</div>

    <template v-else>
      <div class="section-group">
        <div class="group-title">飞龙军 (40级以上)</div>
        <div v-if="dragonArmy.length" class="group-content">
          <div
            v-for="member in dragonArmy"
            :key="member.user_id"
            class="army-item"
          >
            <span class="name">{{ member.nickname || `玩家${member.user_id}` }}</span>
            <span class="level">Lv.{{ member.level || '-' }}</span>
            <span class="score">战功: {{ member.battle_power ?? '-' }}</span>
          </div>
        </div>
        <div v-else class="group-content gray">当前暂无飞龙军成员</div>
      </div>

      <div class="section-group">
        <div class="group-title">伏虎军 (40级及以下)</div>
        <div v-if="tigerArmy.length" class="group-content">
          <div
            v-for="member in tigerArmy"
            :key="member.user_id"
            class="army-item"
          >
            <span class="name">{{ member.nickname || `玩家${member.user_id}` }}</span>
            <span class="level">Lv.{{ member.level || '-' }}</span>
            <span class="score">战功: {{ member.battle_power ?? '-' }}</span>
          </div>
        </div>
        <div v-else class="group-content gray">当前暂无伏虎军成员</div>
      </div>
    </template>

    <div class="section spacer">
      <a class="link" @click.prevent="goWar">返回盟战</a>
    </div>
    <div class="section">
      <a class="link" @click.prevent="goAlliance">返回联盟</a>
    </div>
    <div class="section">
      <a class="link" @click.prevent="goHome">返回游戏首页</a>
    </div>

  </div>
</template>

<style scoped>
.barracks-page {
  background: #fff8dc;
  min-height: 100vh;
  padding: 10px 14px 24px;
  font-size: 13px;
  line-height: 1.7;
  font-family: SimSun, '宋体', serif;
}

.section {
  margin: 6px 0;
}

.title-row {
  font-weight: bold;
  font-size: 15px;
}

.section-group {
  border: 1px solid #e2c48f;
  background: #fff3bf;
  padding: 8px;
  margin-top: 12px;
}

.group-title {
  font-weight: bold;
  margin-bottom: 6px;
}

.group-content {
  padding-left: 8px;
}

.army-item {
  display: flex;
  gap: 10px;
}

.name {
  color: #0066cc;
}

.level {
  color: #c05000;
}

.score {
  color: #333;
}

.link {
  color: #0066cc;
  cursor: pointer;
}

.link:hover {
  text-decoration: underline;
}

.gray {
  color: #777;
}

.small {
  font-size: 11px;
}

.footer {
  margin-top: 24px;
}

.spacer {
  margin-top: 16px;
}

.red {
  color: #cc0000;
}
</style>
