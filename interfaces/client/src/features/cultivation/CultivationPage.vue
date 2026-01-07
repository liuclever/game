<template>
  <div class="page">
    <div class="header">
      <router-link to="/" class="back-link">[返回]</router-link>
      <span class="title">【修行】</span>
    </div>

    <div class="content">
      <!-- 修行状态 -->
      <div class="status-section">
        <div class="label">修行状态：</div>
        <div v-if="loading">加载中...</div>
        <div v-else-if="!status.is_cultivating" class="idle">
          <span class="status-text">空闲中</span>
        </div>
        <div v-else class="cultivating">
          <div>正在 <span class="highlight">{{ status.area }}-{{ status.dungeon }}</span> 修行</div>
          <div>已修行：<span class="highlight">{{ formatDuration(status.elapsed_seconds) }}</span></div>
          <div>有效时间：<span class="highlight">{{ status.effective_minutes }}</span> 分钟</div>
          <div class="preview-rewards" v-if="status.preview_rewards">
            <div>预计获得：</div>
            <div>- 声望: {{ status.preview_rewards.prestige }}</div>
            <div>- 强化石: {{ status.preview_rewards.spirit_stones }}</div>
            <div v-for="beast in status.preview_rewards.beast_exp" :key="beast.name">
              - {{ beast.name }} 经验: {{ beast.exp }}
            </div>
          </div>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="actions">
        <template v-if="!status.is_cultivating">
          <div v-if="!canCultivate" class="warning">
            {{ availableMessage }}
          </div>
          <div v-else>
            <div class="dungeon-select">
              <div class="label">选择副本：</div>
              <div class="duration-select">
                <div class="label">选择时长：</div>
                <span class="link" @click="setDuration(2)">[2小时]</span>
                <span class="link" @click="setDuration(4)">[4小时]</span>
                <span class="link" @click="setDuration(8)">[8小时]</span>
                <span v-if="vipLevel >= 2" class="link" @click="setDuration(12)">[12小时(VIP2)]</span>
                <span v-if="vipLevel >= 4" class="link" @click="setDuration(24)">[24小时(VIP4)]</span>
                <span class="drop-hint">当前：{{ selectedDurationHours }}小时</span>
              </div>
              <div v-for="dungeon in dungeons" :key="dungeon.name" class="dungeon-item">
                <span 
                  class="link" 
                  @click="startCultivation(dungeon.name)"
                >
                  [{{ dungeon.name }}]
                </span>
                <span class="drop-hint" v-if="dungeon.capture_balls.length > 0">
                  (2小时+有15%几率获得召唤球)
                </span>
              </div>
            </div>
          </div>
        </template>
        <template v-else>
          <span v-if="status.can_harvest" class="link" @click="endCultivation">[修行收获]</span>
          <span v-else class="link" @click="stopCultivation">[终止修行]</span>
        </template>
      </div>

      <!-- 修行规则说明 -->
      <div class="rules-section">
        <div class="section-title">【修行说明】</div>
        <ul>
          <li>只有定老城及以上地图才能修行</li>
          <li>必须修行满对应时间才可获得预计奖励</li>
          <li>幻兽等级高于人物5级，无法获得幻兽经验</li>
          <li>修行12小时需VIP2，24小时需VIP4</li>
        </ul>
      </div>

      <!-- 当前地图奖励率 -->
      <div v-if="canCultivate" class="rate-section">
        <div class="section-title">【当前地图奖励率】</div>
        <div>地图：{{ areaName }}</div>
        <div>声望/分钟：{{ prestigeRate }}</div>
        <div>幻兽经验/分钟：{{ beastExpRate }}</div>
        <div>强化石/分钟：{{ stoneRate }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import http from '@/services/http.js'

const loading = ref(true)
const status = ref({})
const canCultivate = ref(false)
const availableMessage = ref('')
const dungeons = ref([])
const areaName = ref('')
const prestigeRate = ref(0)
const beastExpRate = ref(0)
const stoneRate = ref(0)
const selectedDurationHours = ref(2)

const vipLevel = computed(() => Number(status.value?.vip_level || 0))

const setDuration = (hours) => {
  selectedDurationHours.value = Number(hours) || 2
  console.log('[cultivation.setDuration] selectedDurationHours=', selectedDurationHours.value)
}

const formatDuration = (seconds) => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60
  if (hours > 0) {
    return `${hours}小时${minutes}分${secs}秒`
  } else if (minutes > 0) {
    return `${minutes}分${secs}秒`
  }
  return `${secs}秒`
}

const fetchStatus = async () => {
  try {
    const res = await http.get('/cultivation/status')
    if (res.data.ok !== false) {
      status.value = res.data
    }
  } catch (e) {
    console.error('获取修行状态失败', e)
  }
}

const fetchAvailableDungeons = async () => {
  try {
    const res = await http.get('/cultivation/available-dungeons')
    if (res.data.ok) {
      canCultivate.value = res.data.can_cultivate
      availableMessage.value = res.data.message || ''
      dungeons.value = res.data.dungeons || []
      areaName.value = res.data.area_name || ''
      prestigeRate.value = res.data.prestige_rate || 0
      beastExpRate.value = res.data.beast_exp_rate || 0
      stoneRate.value = res.data.stone_rate || 0
    }
  } catch (e) {
    console.error('获取可修行副本失败', e)
  }
}

const startCultivation = async (dungeonName) => {
  try {
    console.log('[cultivation.start] selectedDurationHours=', selectedDurationHours.value)
    const res = await http.post('/cultivation/start', {
      area_name: areaName.value,
      dungeon_name: dungeonName,
      duration_hours: selectedDurationHours.value,
      hours: selectedDurationHours.value
    })
    console.log('[cultivation.start] response:', res.data)
    if (res.data.ok) {
      const requested = res.data.requested_duration_hours ?? selectedDurationHours.value
      const applied = res.data.applied_duration_hours ?? selectedDurationHours.value
      const vip = res.data.vip_level ?? vipLevel.value
      alert(`${res.data.message}\nrequested=${requested}h, applied=${applied}h, vip=${vip}`)
      await fetchStatus()
    } else {
      alert(res.data.error || '开始修行失败')
    }
  } catch (e) {
    alert('开始修行失败')
    console.error(e)
  }
}

const endCultivation = async () => {
  try {
    const res = await http.post('/cultivation/end')
    if (res.data.ok) {
      const rewards = res.data.rewards
      let msg = `修行完成！\n获得声望: ${rewards.prestige}\n获得强化石: ${rewards.spirit_stones}`
      if (rewards.beasts && rewards.beasts.length > 0) {
        msg += '\n幻兽经验:'
        rewards.beasts.forEach(b => {
          msg += `\n  ${b.name}: +${b.exp_gain}`
          if (b.leveled_up) msg += ' (升级!)'
        })
      }
      if (rewards.items && rewards.items.length > 0) {
        msg += '\n获得物品: ' + rewards.items.join(', ')
      }
      alert(msg)
      await fetchStatus()
      await fetchAvailableDungeons()
    } else {
      alert(res.data.error || '结束修行失败')
      await fetchStatus()
    }
  } catch (e) {
    alert('结束修行失败')
    console.error(e)
  }
}

const stopCultivation = async () => {
  try {
    const res = await http.post('/cultivation/stop')
    if (res.data.ok) {
      alert(res.data.message || '已终止修行')
      await fetchStatus()
      await fetchAvailableDungeons()
    } else {
      alert(res.data.error || '终止修行失败')
      await fetchStatus()
    }
  } catch (e) {
    alert('终止修行失败')
    console.error(e)
  }
}

onMounted(async () => {
  await fetchStatus()
  await fetchAvailableDungeons()
  loading.value = false
})
</script>

<style scoped>
.page {
  padding: 8px;
  font-size: 14px;
}

.header {
  margin-bottom: 12px;
}

.back-link {
  color: #0033cc;
  text-decoration: none;
  margin-right: 8px;
}

.title {
  font-weight: bold;
}

.content {
  line-height: 1.8;
}

.status-section {
  margin-bottom: 16px;
  padding: 8px;
  border: 1px solid #ddd;
}

.label {
  font-weight: bold;
  margin-bottom: 4px;
}

.status-text {
  color: #666;
}

.cultivating {
  color: #333;
}

.highlight {
  color: #c00;
  font-weight: bold;
}

.preview-rewards {
  margin-top: 8px;
  padding: 8px;
  background: #f9f9f9;
  border-radius: 4px;
}

.actions {
  margin-bottom: 16px;
}

.warning {
  color: #c00;
}

.dungeon-select {
  margin-top: 8px;
}

.dungeon-item {
  margin: 4px 0;
}

.drop-hint {
  color: #999;
  font-size: 12px;
}

.link {
  color: #0033cc;
  cursor: pointer;
}

.link:hover {
  text-decoration: underline;
}

.rules-section, .rate-section {
  margin-top: 16px;
  padding: 8px;
  background: #f5f5f5;
  border-radius: 4px;
}

.section-title {
  font-weight: bold;
  margin-bottom: 8px;
}

ul {
  margin: 0;
  padding-left: 20px;
}

li {
  margin: 4px 0;
}
</style>
