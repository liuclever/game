<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()

// ========== 加载状态 ==========
const loading = ref(true)
const errorMsg = ref('')
const operating = ref(false)

// ========== 化仙池信息 ==========
const huaxianPool = ref({
  level: 1,
  currentExp: 0,
  capacity: 0,
  isFull: false,
})

// ========== 化仙阵信息 ==========
const formation = ref({
  active: false,
  level: 0,
  remainingSeconds: 0,
  hourlyExp: 0,
  pendingExp: 0,
})

// ========== 化仙丹数量 ==========
const huaxianDanCount = ref(0)

// ========== 幻兽列表 ==========
const beastList = ref([])
const teamBeastIds = ref(new Set())

// 所有幻兽（用于化仙列表展示）
const allBeasts = computed(() => {
  return beastList.value.map(beast => {
    // 检查是否在战斗队
    const inTeam = teamBeastIds.value.has(beast.id)
    // 检查是否可化仙（等级>=15且不在战斗队）
    const canHuaxian = beast.level >= 15 && !inTeam
    // 构建显示名称：名字-境界
    let displayName = beast.name || beast.nickname || '未知'
    if (beast.realm && beast.realm !== '地界') {
      displayName = `${displayName}-${beast.realm}`
    }
    return {
      ...beast,
      inTeam,
      canHuaxian,
      displayName,
    }
  })
})

// 可化仙的幻兽数量
const huaxianBeastCount = computed(() => {
  return allBeasts.value.filter(b => b.canHuaxian).length
})

// ========== 加载数据 ==========
const loadData = async () => {
  loading.value = true
  errorMsg.value = ''
  try {
    // 并行获取：幻兽列表、化仙池状态、背包物品
    const [beastRes, poolRes, invRes] = await Promise.all([
      http.get('/beast/list'),
      http.get('/immortalize/status'),
      http.get('/inventory/list'),
    ])
    
    // 幻兽列表
    if (beastRes.data.ok) {
      beastList.value = beastRes.data.beastList || []
      const teamBeasts = beastRes.data.teamBeasts || []
      teamBeastIds.value = new Set(teamBeasts.map(b => b.id))
    }
    
    // 化仙池状态
    if (poolRes.data.ok) {
      huaxianPool.value = {
        level: poolRes.data.level || 1,
        currentExp: poolRes.data.current_exp || 0,
        capacity: poolRes.data.capacity || 0,
        isFull: poolRes.data.is_full || false,
      }
      // 化仙阵状态
      const fm = poolRes.data.formation || {}
      formation.value = {
        active: fm.active || false,
        level: fm.level || 0,
        remainingSeconds: fm.remaining_seconds || 0,
        hourlyExp: fm.hourly_exp || 0,
        pendingExp: fm.pending_exp || 0,
      }
    }
    
    // 背包中的化仙丹数量（item_id = 6015）
    if (invRes.data.ok) {
      const items = invRes.data.items || []
      const danItem = items.find(i => i.item_id === 6015)
      huaxianDanCount.value = danItem ? danItem.quantity : 0
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

// ========== 操作 ==========
// 化仙（转化幻兽为经验）
const doHuaxian = async (beast) => {
  if (!beast.canHuaxian) {
    alert('该幻兽无法化仙')
    return
  }
  const name = beast.displayName || beast.name
  operating.value = true
  try {
    const res = await http.delete(`/beast/${beast.id}`)
    if (res.data.ok) {
      const expAdded = res.data.pool_exp_added || 0
      alert(`【${name}】已化仙，获得经验 ${expAdded}！`)
      await loadData()
    } else {
      alert(res.data.error || '化仙失败')
    }
  } catch (err) {
    alert('网络错误，请稍后重试')
  } finally {
    operating.value = false
  }
}

// 升级化仙池
const upgradePool = () => {
  router.push('/huaxian/upgrade')
}

// 分配经验
const allocateExp = () => {
  router.push('/huaxian/allocate')
}

// 开启化仙阵
const startFormation = async () => {
  if (formation.value.active) {
    alert('化仙阵已在运行中')
    return
  }
  operating.value = true
  try {
    const res = await http.post('/immortalize/formation/start')
    if (res.data.ok) {
      alert('化仙阵已开启！')
      await loadData()
    } else {
      alert(res.data.error || '开启失败')
    }
  } catch (err) {
    alert('网络错误，请稍后重试')
  } finally {
    operating.value = false
  }
}

// 收获经验（化仙阵产生的经验由后台定时结算，这里刷新状态即可）
const harvestExp = async () => {
  await loadData()
  if (formation.value.pendingExp > 0) {
    alert(`已收获 ${formation.value.pendingExp} 经验！`)
  } else {
    alert('暂无可收获的经验')
  }
}

// 使用化仙丹
const useHuaxianDan = async () => {
  if (huaxianDanCount.value <= 0) {
    alert('没有化仙丹可使用')
    return
  }
  operating.value = true
  try {
    const res = await http.post('/immortalize/dan/use', { quantity: 1 })
    if (res.data.ok) {
      alert(res.data.message || '使用成功')
      await loadData()
    } else {
      alert(res.data.error || '使用失败')
    }
  } catch (err) {
    alert('网络错误，请稍后重试')
  } finally {
    operating.value = false
  }
}

// 购买化仙丹
const buyHuaxianDan = () => {
  router.push('/shop')
}

// 查看简介
const viewIntro = () => {
  alert('化仙池简介：\n\n化仙池可以将幻兽转化为经验，用于提升其他幻兽的等级。\n\n战斗队中的幻兽和等级未满15级的幻兽无法进行化仙。')
}

// ========== 导航 ==========
const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="huaxian-page">
    <!-- 加载状态 -->
    <div v-if="loading" class="section">加载中...</div>
    <div v-else-if="errorMsg" class="section" style="color: red;">{{ errorMsg }}</div>
    
    <template v-if="!loading">
      <!-- 化仙池标题 -->
      <div class="section title">
        【化仙池】<a class="link" @click="viewIntro">简介</a>
      </div>
      
      <!-- 品级 -->
      <div class="section">
        品级：<span class="bold">{{ huaxianPool.level }}级</span> <a class="link" @click="upgradePool">升级</a>
      </div>
      
      <!-- 经验池 -->
      <div class="section">
        经验池：<span class="bold">{{ huaxianPool.currentExp }}/{{ huaxianPool.capacity }}</span> <a class="link" @click="allocateExp">分配</a>
      </div>
      
      <!-- 化仙阵 -->
      <div class="section spacer">
        化仙阵：<template v-if="formation.active">运行中({{ Math.ceil(formation.remainingSeconds / 60) }}分钟)</template><template v-else>未开启</template>
        <a v-if="!formation.active" class="link" :class="{ disabled: operating }" @click="startFormation">开启</a>
        <a class="link" @click="harvestExp">收获</a>
      </div>
      
      <!-- 化仙丹 -->
      <div class="section">
        化仙丹 x {{ huaxianDanCount }} <a class="link" :class="{ disabled: operating }" @click="useHuaxianDan">使用</a> · <a class="link" @click="buyHuaxianDan">购买</a>
      </div>
      
      <!-- 幻兽化仙 -->
      <div class="section spacer title">
        幻兽化仙：幻兽消失转化为经验
      </div>
      
      <template v-if="allBeasts.length > 0">
        <div v-for="beast in allBeasts" :key="beast.id" class="section">
          <a class="link beast-name">{{ beast.displayName }}</a>({{ beast.level }}级)
          <span v-if="beast.inTeam" class="gray">(出战中)</span>
          <a 
            v-if="beast.canHuaxian" 
            class="link" 
            :class="{ disabled: operating }" 
            @click="doHuaxian(beast)"
          >化仙</a>
          <span v-else class="gray">化仙</span>
        </div>
      </template>
      <div v-else class="section gray">
        暂无可化仙的幻兽
      </div>
      
      <!-- 提示 -->
      <div class="section spacer gray">
        战斗队及未满15级幻兽无法化仙
      </div>
    </template>

    <!-- 返回 -->
    <div class="section spacer">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>

  </div>
</template>

<style scoped>
.huaxian-page {
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

.beast-name {
  color: #0066CC;
}

.gray {
  color: #666666;
}

.bold {
  font-weight: bold;
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
