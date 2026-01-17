<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()

// ========== 加载状态 ==========
const loading = ref(true)
const errorMsg = ref('')
const upgrading = ref(false)

// ========== 升级信息 ==========
const upgradeInfo = ref({
  canUpgrade: false,
  currentLevel: 1,
  toLevel: 2,
  requiredPlayerLevel: 0,
  playerLevel: 0,
  levelEnough: false,
  materials: [],
})

// ========== 配置信息 ==========
const configInfo = ref({
  poolCapacity: {},
  formationHourlyExp: {},
  danExp: [],
  beastRatio: {},
})

// ========== 加载数据 ==========
const loadData = async () => {
  loading.value = true
  errorMsg.value = ''
  try {
    // 并行获取升级材料和配置
    const [upgradeRes, configRes] = await Promise.all([
      http.get('/immortalize/upgrade/cost'),
      http.get('/immortalize/config'),
    ])
    
    if (upgradeRes.data.ok) {
      upgradeInfo.value = {
        canUpgrade: upgradeRes.data.can_upgrade,
        currentLevel: upgradeRes.data.current_level,
        toLevel: upgradeRes.data.to_level,
        requiredPlayerLevel: upgradeRes.data.required_player_level,
        playerLevel: upgradeRes.data.player_level,
        levelEnough: upgradeRes.data.level_enough,
        materials: upgradeRes.data.materials || [],
      }
    } else {
      errorMsg.value = upgradeRes.data.error || '加载升级信息失败'
    }
    
    if (configRes.data.ok) {
      // 解析配置
      const danExpList = configRes.data.dan_exp || []
      const danExpMap = {}
      danExpList.forEach(item => {
        danExpMap[item.level] = item.exp
      })
      
      configInfo.value = {
        poolCapacity: configRes.data.pool_capacity || {},
        formationHourlyExp: configRes.data.formation_hourly_exp || {},
        danExp: danExpMap,
        beastRatio: configRes.data.beast_ratio || {},
      }
    }
  } catch (err) {
    errorMsg.value = '网络错误，请稍后重试'
    console.error('加载数据失败:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})

// ========== 计算属性 ==========
// 当前等级容量
const currentCapacity = computed(() => {
  return configInfo.value.poolCapacity[upgradeInfo.value.currentLevel] || 0
})

// 下一等级容量
const nextCapacity = computed(() => {
  return configInfo.value.poolCapacity[upgradeInfo.value.toLevel] || 0
})

// 当前等级化仙阵经验
const currentFormationExp = computed(() => {
  return configInfo.value.formationHourlyExp[upgradeInfo.value.currentLevel] || 0
})

// 下一等级化仙阵经验
const nextFormationExp = computed(() => {
  return configInfo.value.formationHourlyExp[upgradeInfo.value.toLevel] || 0
})

// 当前等级化仙丹经验
const currentDanExp = computed(() => {
  return configInfo.value.danExp[upgradeInfo.value.currentLevel] || 0
})

// 下一等级化仙丹经验
const nextDanExp = computed(() => {
  return configInfo.value.danExp[upgradeInfo.value.toLevel] || 0
})

// 当前幻兽化仙加成
const currentBeastRatio = computed(() => {
  const ratio = configInfo.value.beastRatio[upgradeInfo.value.currentLevel] || 0
  return (ratio * 100).toFixed(1)
})

// 下一等级幻兽化仙加成
const nextBeastRatio = computed(() => {
  const ratio = configInfo.value.beastRatio[upgradeInfo.value.toLevel] || 0
  return (ratio * 100).toFixed(1)
})

// 是否已达最高等级
const isMaxLevel = computed(() => {
  return !upgradeInfo.value.toLevel
})

// 铜钱材料（最后一个）
const copperMaterial = computed(() => {
  const mats = upgradeInfo.value.materials
  return mats.find(m => m.item_id === 0)
})

// 结晶材料（除铜钱外）
const crystalMaterials = computed(() => {
  return upgradeInfo.value.materials.filter(m => m.item_id !== 0)
})

// ========== 操作 ==========
const doUpgrade = async () => {
  if (!upgradeInfo.value.canUpgrade) {
    alert('升级条件不满足')
    return
  }
  upgrading.value = true
  try {
    const res = await http.post('/immortalize/upgrade')
    if (res.data.ok) {
      alert(`升级成功！化仙池已升至${res.data.new_level}级`)
      router.push('/huaxian')
    } else {
      alert(res.data.error || '升级失败')
    }
  } catch (err) {
    alert('网络错误，请稍后重试')
    console.error('升级失败:', err)
  } finally {
    upgrading.value = false
  }
}

// ========== 导航 ==========
const goBack = () => {
  router.push('/huaxian')
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="upgrade-page">
    <!-- 加载状态 -->
    <div v-if="loading" class="section">加载中...</div>
    <div v-else-if="errorMsg" class="section" style="color: red;">{{ errorMsg }}</div>
    
    <template v-else>
      <!-- 标题 -->
      <div class="section title">化仙池升级</div>
      
      <!-- 已达最高等级 -->
      <template v-if="isMaxLevel">
        <div class="section">品级：{{ upgradeInfo.currentLevel }}级（已达最高等级）</div>
      </template>
      
      <!-- 升级信息 -->
      <template v-else>
        <div class="section">品级：{{ upgradeInfo.currentLevel }}→{{ upgradeInfo.toLevel }}</div>
        <div class="section">经验池上限:{{ currentCapacity }}→{{ nextCapacity }}</div>
        <div class="section">化仙阵经验:{{ currentFormationExp }}→{{ nextFormationExp }}(每小时)</div>
        <div class="section">化仙丹经验:{{ currentDanExp }}→{{ nextDanExp }}</div>
        <div class="section">幻兽化仙加成:{{ currentBeastRatio }}%→{{ nextBeastRatio }}%</div>
        
        <!-- 要求 -->
        <div class="section spacer title">要求：</div>
        
        <!-- 玩家等级 -->
        <div class="section">
          人物等级达到{{ upgradeInfo.requiredPlayerLevel }}
          <span :class="upgradeInfo.levelEnough ? 'green' : 'red'">
            ({{ upgradeInfo.levelEnough ? '满足' : '不满足' }})
          </span>
        </div>
        
        <!-- 结晶材料 -->
        <div v-for="mat in crystalMaterials" :key="mat.item_id" class="section">
          {{ mat.name }}×{{ mat.required }}
          <span :class="mat.has_enough ? 'green' : 'red'">
            ({{ mat.has_enough ? '满足' : '不满足' }})
          </span>
        </div>
        
        <!-- 铜钱 -->
        <div v-if="copperMaterial" class="section">
          铜钱x{{ copperMaterial.required }}
          <span :class="copperMaterial.has_enough ? 'green' : 'red'">
            ({{ copperMaterial.has_enough ? '满足' : '不满足' }})
          </span>
        </div>
        
        <!-- 升级按钮 -->
        <div class="section spacer">
          <a 
            class="link" 
            :class="{ disabled: !upgradeInfo.canUpgrade || upgrading }"
            @click="doUpgrade"
          >
            {{ upgrading ? '升级中...' : '确认升级' }}
          </a>
        </div>
      </template>
      
      <!-- 导航 -->
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
.upgrade-page {
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
  margin-top: 12px;
  margin-bottom: 4px;
}

.title:first-child {
  margin-top: 0;
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

.link.disabled {
  color: #999999;
  cursor: not-allowed;
}

.red {
  color: #CC0000;
}

.green {
  color: #009900;
}

.gray {
  color: #666666;
}
</style>
