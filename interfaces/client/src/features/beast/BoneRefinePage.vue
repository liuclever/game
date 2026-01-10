<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()

// ========== 数据状态 ==========
const loading = ref(true)
const errorMsg = ref('')
const previewData = ref(null)
const isMaxStage = ref(false)

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
  41: '白金', 42: '白金', 43: '白金', 44: '白金', 45: '白金',
  46: '白金', 47: '白金', 48: '白金', 49: '白金', 50: '白金',
  51: '钻石', 52: '钻石', 53: '钻石', 54: '钻石', 55: '钻石',
  56: '钻石', 57: '钻石', 58: '钻石', 59: '钻石', 60: '钻石',
  61: '星耀', 62: '星耀', 63: '星耀', 64: '星耀', 65: '星耀',
  66: '星耀', 67: '星耀', 68: '星耀', 69: '星耀', 70: '星耀',
  71: '龙晶', 72: '龙晶', 73: '龙晶', 74: '龙晶', 75: '龙晶',
  76: '龙晶', 77: '龙晶', 78: '龙晶', 79: '龙晶', 80: '龙晶',
}

// ========== 计算属性 ==========
const currentStarsDisplay = computed(() => {
  if (!previewData.value?.bone) return ''
  return '★'.repeat(previewData.value.bone.currentStars)
})

const nextStarsDisplay = computed(() => {
  if (!previewData.value?.bone) return ''
  return '★'.repeat(previewData.value.bone.nextStars)
})

const currentLevelDisplay = computed(() => {
  if (!previewData.value?.bone) return ''
  const level = previewData.value.bone.currentLevel
  const tierName = levelNames[level] || '龙晶'
  return `${tierName}${level}级`
})

const nextLevelDisplay = computed(() => {
  if (!previewData.value?.bone) return ''
  const level = previewData.value.bone.nextLevel
  const tierName = levelNames[level] || '龙晶'
  return `${tierName}${level}级`
})

// ========== 加载数据 ==========
const loadPreview = async () => {
  loading.value = true
  errorMsg.value = ''
  
  const boneId = route.params.boneId
  if (!boneId) {
    errorMsg.value = '无效的战骨ID'
    loading.value = false
    return
  }
  
  try {
    const res = await http.get(`/bone/${boneId}/refine-preview`)
    if (res.data.ok) {
      previewData.value = res.data
    } else {
      if (res.data.isMaxStage) {
        isMaxStage.value = true
      }
      errorMsg.value = res.data.error || '加载失败'
    }
  } catch (err) {
    const errorMessage = err.response?.data?.error || '网络错误，请稍后重试'
    errorMsg.value = errorMessage
    console.error('加载炼制预览失败:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadPreview()
})

// ========== 操作 ==========
const doRefine = async () => {
  if (!previewData.value?.canRefine) {
    alert(previewData.value?.reason || '条件不满足')
    return
  }
  
  const boneId = route.params.boneId
  try {
    const res = await http.post(`/bone/${boneId}/refine`)
    if (res.data.ok) {
      alert(res.data.message || '炼制成功！')
      // 返回战骨详情页
      router.push(`/bone/${boneId}`)
    } else {
      alert(res.data.error || '炼制失败')
    }
  } catch (err) {
    const errorMessage = err.response?.data?.error || '网络错误，请稍后重试'
    alert(errorMessage)
    console.error('炼制战骨失败:', err)
  }
}

// ========== 导航 ==========
const goBack = () => {
  router.back()
}

const goToBone = () => {
  router.push(`/bone/${route.params.boneId}`)
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="bone-refine-page">
    <!-- 加载状态 -->
    <div v-if="loading" class="section">加载中...</div>
    <div v-else-if="isMaxStage" class="section">
      已达最高阶段，无法继续炼制
      <div class="section spacer">
        <a class="link" @click="goBack">返回战骨</a>
      </div>
    </div>
    <div v-else-if="errorMsg" class="section error">{{ errorMsg }}</div>
    
    <!-- 炼制预览 -->
    <template v-else-if="previewData">
      <!-- 战骨名称变化 -->
      <div class="section">
        战骨名称:{{ previewData.bone.currentName }}→{{ previewData.bone.nextName }}
      </div>
      
      <!-- 星级变化 -->
      <div class="section">
        星级:{{ currentStarsDisplay }}→{{ nextStarsDisplay }}
      </div>
      
      <!-- 强化等级变化 -->
      <div class="section">
        强化等级:{{ currentLevelDisplay }}→{{ nextLevelDisplay }}
      </div>
      
      <!-- 属性变化 -->
      <div class="section">属性:</div>
      <div class="section" v-if="previewData.bone.currentStats.hp > 0 || previewData.bone.nextStats.hp > 0">
        气血+{{ previewData.bone.currentStats.hp }}→{{ previewData.bone.nextStats.hp }}
      </div>
      <div class="section" v-if="previewData.bone.currentStats.attack > 0 || previewData.bone.nextStats.attack > 0">
        攻击+{{ previewData.bone.currentStats.attack }}→{{ previewData.bone.nextStats.attack }}
      </div>
      <div class="section" v-if="previewData.bone.currentStats.physicalDefense > 0 || previewData.bone.nextStats.physicalDefense > 0">
        物防+{{ previewData.bone.currentStats.physicalDefense }}→{{ previewData.bone.nextStats.physicalDefense }}
      </div>
      <div class="section" v-if="previewData.bone.currentStats.magicDefense > 0 || previewData.bone.nextStats.magicDefense > 0">
        法防+{{ previewData.bone.currentStats.magicDefense }}→{{ previewData.bone.nextStats.magicDefense }}
      </div>
      <div class="section" v-if="previewData.bone.currentStats.speed > 0 || previewData.bone.nextStats.speed > 0">
        速度+{{ previewData.bone.currentStats.speed }}→{{ previewData.bone.nextStats.speed }}
      </div>
      
      <!-- 需求等级 -->
      <div class="section">
        需求等级:{{ previewData.requiredLevel }}
      </div>
      
      <!-- 需求材料 -->
      <div class="section">需求材料:</div>
      <div class="section" v-for="(material, index) in previewData.materials" :key="index">
        {{ material.name }}({{ material.owned }}/{{ material.required }})
      </div>
      
      <!-- 炼制按钮 -->
      <div class="section">
        <a class="link" @click="doRefine">确定炼制</a>
      </div>
      
      <!-- 导航 -->
      <div class="section spacer">
        <a class="link" @click="goToBone">返回战骨</a>
      </div>
      <div class="section">
        <a class="link" @click="goHome">返回游戏首页</a>
      </div>
    </template>
    
  </div>
</template>

<style scoped>
.bone-refine-page {
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
