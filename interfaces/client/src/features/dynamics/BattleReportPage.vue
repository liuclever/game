<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()

const loading = ref(true)
const error = ref('')
const battleData = ref(null)
const selectedBattleIndex = ref(0)

const battleType = computed(() => route.query.type || '')
const battleId = computed(() => route.query.id || '')

const loadBattle = async () => {
  if (!battleId.value) {
    error.value = '缺少战报ID'
    loading.value = false
    return
  }

  loading.value = true
  error.value = ''
  
  try {
    let apiUrl = ''
    switch (battleType.value) {
      case 'arena':
        apiUrl = `/arena/battle/${battleId.value}`
        break
      case 'zhenyao':
        apiUrl = `/tower/zhenyao/battle/${battleId.value}`
        break
      case 'battlefield':
        apiUrl = `/battlefield/battle/${battleId.value}`
        break
      case 'spar':
        // 切磋战报暂时不支持（需要实现API端点）
        error.value = '切磋战报详情功能暂未实现'
        loading.value = false
        return
      default:
        error.value = '未知的战斗类型'
        loading.value = false
        return
    }
    
    const res = await http.get(apiUrl)
    if (res.data.ok) {
      battleData.value = res.data.battle || res.data
    } else {
      error.value = res.data.error || '加载战报失败'
    }
  } catch (e) {
    console.error('加载战报失败', e)
    error.value = e.response?.data?.error || '加载战报失败'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadBattle()
})

// 获取战斗数据
const battleDataObj = computed(() => {
  if (!battleData.value) return null
  // 不同API返回的数据结构可能不同
  if (battleData.value.battle_data) {
    return battleData.value.battle_data
  }
  return battleData.value
})

// 获取所有战斗
const battles = computed(() => {
  const data = battleDataObj.value
  if (!data) return []
  return data.battles || []
})

// 当前显示的战斗
const currentBattle = computed(() => {
  if (battles.value.length === 0) return null
  const index = Math.min(selectedBattleIndex.value, battles.value.length - 1)
  return battles.value[index]
})

// 英雄天赋（如果有）
const heroTalents = computed(() => {
  const data = battleDataObj.value
  if (!data) return []
  return data.hero_talents || []
})

const switchBattle = (index) => {
  selectedBattleIndex.value = index
}

const goBack = () => {
  router.back()
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="report-page">
    <div class="section title">
      【详细战报】 <a class="link" @click="goBack">返回</a>
    </div>

    <div v-if="loading" class="section">加载中...</div>
    <div v-else-if="error" class="section red">{{ error }}</div>

    <template v-else-if="battleDataObj">
      <!-- 多战切换导航 -->
      <div v-if="battles.length > 1" class="section">
        <template v-for="(b, index) in battles" :key="index">
          <a 
            class="link battle-tab" 
            :class="{ active: selectedBattleIndex === index }"
            @click="switchBattle(index)"
          >第{{ index + 1 }}战</a>
          <span v-if="index < battles.length - 1"> | </span>
        </template>
      </div>

      <!-- 英雄天赋 -->
      <div v-if="heroTalents.length > 0" class="section">
        <div v-for="(talent, index) in heroTalents" :key="index" class="section">
          [英雄天赋]:{{ talent }}
        </div>
      </div>

      <!-- 当前战斗的回合信息 -->
      <template v-if="currentBattle">
        <div 
          v-for="(round, index) in currentBattle.rounds || []" 
          :key="index" 
          class="section"
        >
          [回合{{ round.round }}]: {{ round.action }}
        </div>
        
        <!-- 战斗结束 -->
        <div v-if="currentBattle.result" class="section result">
          [战斗结束]: {{ currentBattle.result }}
        </div>
      </template>
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
.report-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 16px;
  line-height: 1.6;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 4px 0;
}

.title {
  font-weight: bold;
  margin-bottom: 8px;
}

.link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: underline;
}

.link:hover {
  text-decoration: underline;
}

.battle-tab.active {
  color: #CC3300;
  font-weight: bold;
}

.red {
  color: #CC0000;
}

.green {
  color: #009900;
}

.result {
  margin-top: 8px;
  font-weight: bold;
}

.spacer {
  margin-top: 16px;
}
</style>
