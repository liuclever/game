<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()

// 跳转到战灵详情页
const goToSpiritDetail = (spiritId) => {
  router.push(`/spirit/${spiritId}`)
}

// ========== 数据状态 ==========
const loading = ref(true)
const errorMsg = ref('')
const spirits = ref([])
const warehouseCount = ref(0)
const warehouseCapacity = ref(100)

// 当前选中的元素分类
const currentElement = ref('earth')

// 元素配置
const elementConfig = [
  { key: 'earth', label: '土灵' },
  { key: 'fire', label: '火灵' },
  { key: 'water', label: '水灵' },
  { key: 'wood', label: '木灵' },
  { key: 'metal', label: '金灵' },
  { key: 'god', label: '神灵' },
]

// ========== 加载数据 ==========
const loadData = async () => {
  loading.value = true
  errorMsg.value = ''
  
  try {
    const res = await http.get('/spirit/warehouse')
    if (res.data.ok) {
      spirits.value = res.data.spirits || []
      warehouseCount.value = res.data.count || 0
      warehouseCapacity.value = res.data.capacity || 100
    } else {
      errorMsg.value = res.data.error || '加载失败'
    }
  } catch (err) {
    errorMsg.value = '网络错误，请稍后重试'
    console.error('加载灵件室数据失败:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})

// ========== 计算属性 ==========
// 按当前元素筛选的战灵
const filteredSpirits = computed(() => {
  return spirits.value.filter(sp => sp.element === currentElement.value)
})

// 获取战灵的已解锁属性条数
const getUnlockedLineCount = (spirit) => {
  if (!spirit.lines) return 0
  return spirit.lines.filter(ln => ln.unlocked).length
}

// 获取战灵的总属性条数
const getTotalLineCount = (spirit) => {
  if (!spirit.lines) return 0
  return spirit.lines.length
}

// 判断战灵是否被锁定（任意一条属性被锁定则整个战灵锁定）
const isLocked = (spirit) => {
  if (!spirit.lines) return false
  return spirit.lines.some(ln => ln.locked)
}

// ========== 操作 ==========
const selectElement = (elementKey) => {
  currentElement.value = elementKey
}

const toggleLock = async (spirit) => {
  try {
    // 切换锁定状态：如果当前锁定则解锁，否则锁定
    const newLockState = !isLocked(spirit)
    
    // 锁定/解锁第一条属性来代表整个战灵的锁定状态
    const res = await http.post(`/spirit/${spirit.id}/lock-line`, {
      line_index: 0,
      locked: newLockState
    })
    
    if (res.data.ok) {
      // 更新本地状态
      const idx = spirits.value.findIndex(s => s.id === spirit.id)
      if (idx >= 0 && res.data.spirit && res.data.spirit.lines) {
        spirits.value[idx].lines = res.data.spirit.lines
      }
    } else {
      console.error(res.data.error || '操作失败')
    }
  } catch (err) {
    console.error('网络错误，请稍后重试')
    console.error('锁定/解锁战灵失败:', err)
  }
}

const sellSpirit = async (spirit) => {
  if (isLocked(spirit)) {
    console.error('该战灵已锁定，无法出售')
    return
  }
  
  if (!confirm(`确定要出售 ${spirit.name} 吗？`)) {
    return
  }
  
  try {
    const res = await http.post(`/spirit/${spirit.id}/sell`)
    if (res.data.ok) {
      // 从列表中移除
      spirits.value = spirits.value.filter(s => s.id !== spirit.id)
      warehouseCount.value -= 1
      console.error(`出售成功，获得 ${res.data.spiritPower || 0} 灵力`)
    } else {
      console.error(res.data.error || '出售失败')
    }
  } catch (err) {
    console.error('网络错误，请稍后重试')
    console.error('出售战灵失败:', err)
  }
}

const sellAllUnlocked = async () => {
  const unlockedSpirits = filteredSpirits.value.filter(s => !isLocked(s))
  
  if (unlockedSpirits.length === 0) {
    console.error('没有可出售的战灵（未锁定的）')
    return
  }
  
  if (!confirm(`确定要出售当前分类下所有未锁定的 ${unlockedSpirits.length} 个战灵吗？`)) {
    return
  }
  
  let successCount = 0
  let totalPower = 0
  
  for (const spirit of unlockedSpirits) {
    try {
      const res = await http.post(`/spirit/${spirit.id}/sell`)
      if (res.data.ok) {
        successCount++
        totalPower += res.data.spiritPower || 0
      }
    } catch (err) {
      console.error('出售战灵失败:', err)
    }
  }
  
  // 重新加载数据
  await loadData()
  console.error(`成功出售 ${successCount} 个战灵，获得 ${totalPower} 灵力`)
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
  <div class="warehouse-page">
    <!-- 标题 -->
    <div class="section title-section">
      【灵件室】
    </div>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="section">加载中...</div>
    <div v-else-if="errorMsg" class="section error">{{ errorMsg }}</div>
    
    <template v-else>
      <!-- 元素分类标签 -->
      <div class="section element-tabs">
        <template v-for="(elem, index) in elementConfig" :key="elem.key">
          <a 
            class="link element-tab"
            :class="{ active: elem.key === currentElement }"
            @click="selectElement(elem.key)"
          >{{ elem.label }}</a>
          <span v-if="index < elementConfig.length - 1"> | </span>
        </template>
      </div>
      
      <!-- 一键出售 -->
      <div class="section">
        <a class="link" @click="sellAllUnlocked">一键出售</a>
      </div>
      
      <!-- 战灵列表 -->
      <div class="spirits-section">
        <div v-if="filteredSpirits.length === 0" class="section">
          暂无此类型战灵
        </div>
        <div v-else>
          <div v-for="spirit in filteredSpirits" :key="spirit.id" class="section spirit-row">
            <a class="link spirit-info" :class="{ 'spirit-unlocked': !isLocked(spirit) }" @click="goToSpiritDetail(spirit.id)">
              {{ spirit.name }} ({{ getUnlockedLineCount(spirit) }}条属性)
            </a>
            <a class="link action-btn" @click.prevent="toggleLock(spirit)">
              {{ isLocked(spirit) ? '解锁' : '锁定' }}
            </a>
            <a class="link action-btn" @click.prevent="sellSpirit(spirit)">售出</a>
          </div>
        </div>
      </div>
      
      <!-- 导航 -->
      <div class="section spacer">
        <a class="link" @click="goBack">返回战灵首页</a>
      </div>
      <div class="section">
        <a class="link" @click="goHome">返回游戏首页</a>
      </div>
    </template>
    
  </div>
</template>

<style scoped>
.warehouse-page {
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

.title-section {
  font-weight: bold;
}

.element-tabs {
  margin: 8px 0;
}

.element-tab {
  margin-right: 2px;
}

.element-tab.active {
  color: #000;
  font-weight: bold;
  text-decoration: none;
  cursor: default;
}

.spirit-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.spirit-info {
  color: #0066CC;
}

.spirit-unlocked {
  /* 未锁定的战灵用普通蓝色 */
}

.action-btn {
  color: #0066CC;
  cursor: pointer;
}

.action-btn:hover {
  text-decoration: underline;
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
  font-size: 17px;
}
</style>
