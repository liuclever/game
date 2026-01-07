<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()

// ========== 数据状态 ==========
const loading = ref(true)
const errorMsg = ref('')
const bone = ref(null)

// 强化等级名称映射
const levelNames = {
  1: '黑铁', 2: '黑铁', 3: '黑铁', 4: '黑铁', 5: '黑铁',
  6: '黑铁', 7: '黑铁', 8: '黑铁', 9: '黑铁', 10: '黑铁',
  11: '青铜', 12: '青铜', 13: '青铜', 14: '青铜', 15: '青铜',
  16: '青铜', 17: '青铜', 18: '青铜', 19: '青铜', 20: '青铜',
  21: '白银', 22: '白银', 23: '白银', 24: '白银', 25: '白银',
  26: '白银', 27: '白银', 28: '白银', 29: '白银', 30: '白银',
  31: '黄金', 32: '黄金', 33: '黄金', 34: '黄金', 35: '黄金',
  36: '黄金', 37: '黄金', 38: '黄金', 39: '黄金', 40: '黄金',
}

// 阶段名称映射
const stageNames = {
  1: '原始', 2: '碎空', 3: '猎魔', 4: '龙炎', 5: '奔雷',
  6: '凌霄', 7: '麒麟', 8: '武神', 9: '弑天', 10: '毁灭',
}

// ========== 计算属性 ==========
const boneName = computed(() => {
  if (!bone.value) return ''
  const stageName = stageNames[bone.value.stage] || '原始'
  return `${stageName}${bone.value.slot}`
})

const levelDisplay = computed(() => {
  if (!bone.value) return ''
  const level = bone.value.level
  const tierName = levelNames[level] || '黑铁'
  return `${tierName}${level}级`
})

const starsDisplay = computed(() => {
  if (!bone.value) return ''
  return '★'.repeat(bone.value.stars)
})

// ========== 加载数据 ==========
const loadBoneDetail = async () => {
  loading.value = true
  errorMsg.value = ''
  
  const boneId = route.params.boneId
  if (!boneId) {
    errorMsg.value = '无效的战骨ID'
    loading.value = false
    return
  }
  
  try {
    const res = await http.get(`/bone/${boneId}`)
    if (res.data.ok) {
      bone.value = res.data.bone
    } else {
      errorMsg.value = res.data.error || '加载失败'
    }
  } catch (err) {
    errorMsg.value = '网络错误，请稍后重试'
    console.error('加载战骨详情失败:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadBoneDetail()
})

// ========== 操作 ==========
const goToRefine = () => {
  if (!bone.value) return
  router.push(`/bone/${bone.value.id}/refine`)
}

const upgrade = async () => {
  if (!bone.value) return
  
  try {
    const res = await http.post(`/bone/${bone.value.id}/upgrade`)
    if (res.data.ok) {
      alert(res.data.message || '强化成功')
      await loadBoneDetail()
    } else {
      alert(res.data.error || '强化失败')
    }
  } catch (err) {
    alert('网络错误')
    console.error('强化战骨失败:', err)
  }
}

// ========== 导航 ==========
const goBack = () => {
  router.back()
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="bone-detail-page">
    <!-- 加载状态 -->
    <div v-if="loading" class="section">加载中...</div>
    <div v-else-if="errorMsg" class="section error">{{ errorMsg }}</div>
    
    <!-- 战骨详情 -->
    <template v-else-if="bone">
      <div class="section">
        战骨名称:{{ boneName }}.<a class="link" @click="goToRefine">炼制</a>
      </div>
      <div class="section">
        星级:{{ starsDisplay }}
      </div>
      <div class="section">
        强化等级:{{ levelDisplay }}.<a class="link" @click="upgrade">强化</a>
      </div>
      <div class="section">
        属性:
      </div>
      <div class="section" v-if="bone.hp_flat > 0">
        气血+{{ bone.hp_flat }}
      </div>
      <div class="section" v-if="bone.attack_flat > 0">
        攻击+{{ bone.attack_flat }}
      </div>
      <div class="section" v-if="bone.physical_defense_flat > 0">
        物防+{{ bone.physical_defense_flat }}
      </div>
      <div class="section" v-if="bone.magic_defense_flat > 0">
        法防+{{ bone.magic_defense_flat }}
      </div>
      <div class="section" v-if="bone.speed_flat > 0">
        速度+{{ bone.speed_flat }}
      </div>
    </template>
    
    <!-- 导航 -->
    <div class="section spacer">
      <a class="link" @click="goBack">返回前页</a>
    </div>
    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>
    
  </div>
</template>

<style scoped>
.bone-detail-page {
  background: #FFF8DC;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 13px;
  line-height: 1.6;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 2px 0;
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

.error {
  color: red;
}

.footer {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #ccc;
}

.gray {
  color: #666;
}

.small {
  font-size: 11px;
}
</style>
