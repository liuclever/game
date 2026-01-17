<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()

// 加载状态
const loading = ref(true)
const errorMsg = ref('')

// 幻兽信息
const beastId = ref(0)
const beastName = ref('')
const beastLevel = ref(1)

// 魔魂数据
const mosouls = ref([])
const usedSlots = ref(0)
const maxSlots = ref(6)
const totalSoulPower = ref(0)
const slotUnlockInfo = ref([])

// 加载幻兽魔魂信息
const loadMoSouls = async () => {
  loading.value = true
  errorMsg.value = ''
  
  beastId.value = route.params.id
  if (!beastId.value) {
    errorMsg.value = '无效的幻兽ID'
    loading.value = false
    return
  }
  
  try {
    const res = await http.get(`/mosoul/beast/${beastId.value}`)
    if (res.data.ok) {
      beastName.value = res.data.beast_name
      beastLevel.value = res.data.beast_level
      mosouls.value = res.data.mosouls || []
      usedSlots.value = res.data.used_slots || 0
      maxSlots.value = res.data.max_slots || 6
      totalSoulPower.value = res.data.total_soul_power || 0
      slotUnlockInfo.value = res.data.slot_unlock_info || []
    } else {
      errorMsg.value = res.data.error || '加载失败'
    }
  } catch (err) {
    errorMsg.value = '网络错误，请稍后重试'
    console.error('加载魔魂信息失败:', err)
  } finally {
    loading.value = false
  }
}

// 获取槽位列表（包含已装备和空槽位）
const slots = computed(() => {
  const result = []
  // 创建槽位映射
  const mosoulMap = {}
  mosouls.value.forEach(m => {
    mosoulMap[m.slot_index] = m
  })
  
  // 生成槽位列表
  for (let i = 1; i <= maxSlots.value; i++) {
    const slotInfo = slotUnlockInfo.value.find(s => s.slot_index === i)
    const mosoul = mosoulMap[i]
    
    result.push({
      index: i,
      mosoul: mosoul || null,
      unlocked: slotInfo ? slotInfo.unlocked : true,
      unlockText: slotInfo ? slotInfo.unlock_text : ''
    })
  }
  return result
})

// 第7槽位（70级解锁）
const slot7 = computed(() => {
  const slotInfo = slotUnlockInfo.value.find(s => s.slot_index === 7)
  return {
    unlocked: slotInfo ? slotInfo.unlocked : false,
    unlockText: slotInfo ? slotInfo.unlock_text : '幻兽70级时开启'
  }
})

// 使用魔魂（跳转到选择魔魂页面）
const useMoSoul = (slotIndex) => {
  router.push(`/beast/${beastId.value}/mosoul/select?slot=${slotIndex}`)
}

// 卸下魔魂
const unequipMoSoul = async (mosoul) => {
  try {
    const res = await http.post(`/mosoul/unequip/${mosoul.id}`)
    if (res.data.ok) {
      alert('卸下成功')
      await loadMoSouls()
    } else {
      alert(res.data.error || '卸下失败')
    }
  } catch (err) {
    alert('网络错误，请稍后重试')
    console.error('卸下魔魂失败:', err)
  }
}

// 获取品质对应的颜色
const getGradeColor = (grade) => {
  const colors = {
    'god_soul': '#FFD700',     // 金色 - 神魂
    'dragon_soul': '#9932CC',   // 紫色 - 龙魂
    'heaven_soul': '#FF4500',   // 橙色 - 天魂
    'earth_soul': '#4169E1',    // 蓝色 - 地魂
    'dark_soul': '#32CD32',     // 绿色 - 玄魂
    'yellow_soul': '#808080',   // 灰色 - 黄魂
    'waste_soul': '#A9A9A9',    // 深灰 - 废魂
  }
  return colors[grade] || '#000000'
}

// 查看魔魂详情
const viewMoSoulDetail = (mosoulId) => {
  router.push(`/mosoul/${mosoulId}?beastId=${beastId.value}`)
}

// 摄魂（进入噬魂/升级页面）
const absorbSoul = (mosoulId) => {
  router.push(`/beast/${beastId.value}/mosoul/${mosoulId}/absorb`)
}

// 返回魔魂首页
const goBack = () => {
  router.push(`/beast/${beastId.value}`)
}

// 返回首页
const goHome = () => {
  router.push('/')
}

onMounted(() => {
  loadMoSouls()
})
</script>

<template>
  <div class="mosoul-page">
    <!-- 加载状态 -->
    <div v-if="loading" class="section">加载中...</div>
    <div v-else-if="errorMsg" class="section error">{{ errorMsg }}</div>
    
    <!-- 魔魂信息 -->
    <template v-else>
      <!-- 魂位和魂力 -->
      <div class="section">
        魂位: {{ usedSlots }}/{{ maxSlots }}
      </div>
      <div class="section">
        魂力: {{ totalSoulPower }}
      </div>
      
      <!-- 槽位列表 -->
      <div v-for="slot in slots" :key="slot.index" class="section">
        <template v-if="slot.unlocked">
            <template v-if="slot.mosoul">
              <!-- 已装备魔魂 -->
              {{ slot.index }}: <a class="link" :style="{ color: getGradeColor(slot.mosoul.grade) }" @click="viewMoSoulDetail(slot.mosoul.id)">{{ slot.mosoul.name }}</a>.<a class="link" @click="unequipMoSoul(slot.mosoul)">取下</a>.<a class="link" @click="absorbSoul(slot.mosoul.id)">摄魂</a>
            </template>
          <template v-else>
            <!-- 空槽位 -->
            {{ slot.index }}: 空.<a class="link" @click="useMoSoul(slot.index)">使用</a>
          </template>
        </template>
        <template v-else>
          <!-- 未解锁槽位 -->
          {{ slot.index }}:幻兽{{ slot.unlockText }}
        </template>
      </div>
      

      <!-- 导航 -->
      <div class="section spacer">
        <a class="link" @click="goBack">返回魔魂首页</a>
      </div>
      <div class="section">
        <a class="link" @click="goHome">返回游戏首页</a>
      </div>
      
    </template>
  </div>
</template>

<style scoped>
.mosoul-page {
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
  margin-bottom: 8px;
}

.spacer {
  margin-top: 16px;
}

.spacer-small {
  margin-top: 8px;
}

.error {
  color: red;
}

.link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.mosoul-item {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
}

.mosoul-name {
  font-weight: bold;
}

.mosoul-grade {
  color: #666;
}

.mosoul-level {
  color: #333;
}

.mosoul-effect {
  color: #228B22;
}

.action-btn {
  margin-left: 4px;
}

.locked-slot {
  color: #999;
  font-style: italic;
}

.gray {
  color: #666666;
}

.small {
  font-size: 17px;
}

.footer {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #CCCCCC;
}
</style>
