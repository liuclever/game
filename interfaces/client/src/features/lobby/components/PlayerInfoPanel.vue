<script setup>
import { computed, onMounted, ref } from 'vue'
import http from '@/services/http'

// 个人信息面板：展示当前登录用户的核心数值
const user = ref(null) // /api/auth/status
const cultivation = ref(null) // /api/cultivation/status（用于声望晋级门槛）
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    loading.value = true
    const res = await http.get('/auth/status')
    if (res.data?.logged_in) {
      user.value = res.data
      try {
        const c = await http.get('/cultivation/status')
        if (c.data?.ok) cultivation.value = c.data
      } catch (e) {
        // 忽略修行状态失败：不影响个人信息展示
      }
    } else {
      user.value = null
    }
  } catch (e) {
    console.error(e)
    error.value = '加载玩家信息失败'
  } finally {
    loading.value = false
  }
})

const summonerTitle = computed(() => {
  const lv = Number(user.value?.level || 0)
  if (!Number.isFinite(lv) || lv <= 0) return ''
  const star = Math.floor(lv / 10)
  const pin = lv % 10
  return `${star}星${pin}品召唤师`
})

const prestigeDisplay = computed(() => {
  const cur = Number(user.value?.prestige || 0)
  const required = cultivation.value?.prestige_required
  if (required === null || required === undefined) return String(cur)
  return `${cur}/${Number(required)}`
})
</script>

<template>
  <div class="panel">
    <div class="title">【个人信息】</div>

    <!-- 加载中 / 错误提示 -->
    <div v-if="loading">正在加载...</div>
    <div v-else-if="error">{{ error }}</div>
    <div v-else-if="!user" class="gray">请先登录查看个人信息</div>
    <template v-else>
      <div>等级：{{ summonerTitle }}</div>
      <div>声望：{{ prestigeDisplay }} <span v-if="cultivation?.can_levelup" class="red">可晋级</span></div>
      <div>活力：{{ user.energy }}/{{ user.max_energy }}</div>
      <div>水晶塔：{{ user.crystal_tower || 0 }}/100</div>
      <div>战力：{{ user.battle_power || 0 }}</div>
      <div>铜钱：{{ user.copper || 0 }}</div>
      <div>元宝：{{ user.yuanbao || 0 }}</div>
    </template>
  </div>
</template>

<style scoped>
.panel {
  border: 1px solid #dddddd;
  padding: 4px 8px;
}

.title {
  margin-bottom: 4px;
}

div + div {
  margin-top: 2px;
}

.gray {
  color: #666;
}

.red {
  color: #cc3300;
  font-weight: bold;
}
</style>
