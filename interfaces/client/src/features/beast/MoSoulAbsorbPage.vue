<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()

// 加载状态
const loading = ref(true)
const errorMsg = ref('')

// 目标魔魂（正在升级的那个）
const beastId = ref(0)
const targetMosoulId = ref(0)
const targetMosoul = ref(null)
const fromWarehouse = ref(false)

// 储魂器数据
const warehouseCount = ref(0)
const warehouseCapacity = ref(90)

// 魔魂列表（可选材料）
const mosouls = ref([])

// 分页
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const totalPages = ref(1)

// 品质筛选
const gradeFilter = ref('')
const gradeOptions = [
  { value: '', label: '全部' },
  { value: 'dragon_soul', label: '龙魂' },
  { value: 'heaven_soul', label: '天魂' },
  { value: 'earth_soul', label: '地魂' },
  { value: 'dark_soul', label: '玄魂' },
  { value: 'yellow_soul', label: '黄魂' },
  { value: 'god_soul', label: '神魂' },
]

// 品质对应的经验值
const gradeExpMap = {
  'god_soul': 1000,
  'dragon_soul': 800,
  'heaven_soul': 400,
  'earth_soul': 200,
  'dark_soul': 100,
  'yellow_soul': 50,
  'waste_soul': 0,
}

// 获取材料提供的经验
const getExpProvide = (grade) => {
  return gradeExpMap[grade] || 0
}

const getGradeLabel = (grade) => {
  const opt = gradeOptions.find(o => o.value === grade)
  return opt ? opt.label : grade
}

// 判断目标魔魂是否满级
const isMaxLevel = computed(() => {
  return targetMosoul.value && targetMosoul.value.level >= 10
})

// 加载初始数据
const loadInitialData = async () => {
  loading.value = true
  errorMsg.value = ''
  
  // 支持两种路由格式：
  // 1. /beast/:id/mosoul/:mosoulId/absorb (从幻兽魔魂页面进入)
  // 2. /mosoul/:id/absorb (从储魂器进入)
  if (route.params.mosoulId) {
    beastId.value = route.params.id
    targetMosoulId.value = route.params.mosoulId
    fromWarehouse.value = false
  } else {
    targetMosoulId.value = route.params.id
    fromWarehouse.value = route.query.from === 'warehouse'
  }
  
  try {
    // 加载目标魔魂详情
    const targetRes = await http.get(`/mosoul/${targetMosoulId.value}`)
    if (targetRes.data.ok) {
      targetMosoul.value = targetRes.data.mosoul
      // 如果魔魂已装备在某个幻兽上，记录beastId
      if (targetRes.data.mosoul.beast_id) {
        beastId.value = targetRes.data.mosoul.beast_id
      }
    } else {
      errorMsg.value = targetRes.data.error || '加载目标魔魂失败'
      loading.value = false
      return
    }
    
    // 加载仓库魔魂
    await loadWarehouseData()
  } catch (err) {
    errorMsg.value = '网络错误，请稍后重试'
    console.error('加载详情失败:', err)
  } finally {
    loading.value = false
  }
}

const performBatchAbsorb = async () => {
  if (isMaxLevel.value) {
    alert('目标魔魂已满级，无法继续升级')
    return
  }

  if (!targetMosoul.value) {
    alert('目标魔魂不存在')
    return
  }

  if (!mosouls.value || mosouls.value.length === 0) {
    alert('没有可选的魔魂材料')
    return
  }

  const gradeText = gradeFilter.value ? getGradeLabel(gradeFilter.value) : '全部'
  if (!confirm(`确定要一键噬魂吗？\n\n升级对象：${targetMosoul.value.name}\n材料品质：${gradeText}\n\n注意：将消耗储魂器内所有符合条件的魔魂（不含升级对象），材料魔魂会消失！\n目标满级后，剩余材料仍会被吞噬（经验会浪费）。`)) {
    return
  }

  try {
    const res = await http.post('/mosoul/consume/batch', {
      targetMosoulId: targetMosoulId.value,
      grade: gradeFilter.value,
    })

    if (res.data.ok) {
      alert(res.data.message || '一键噬魂成功')
      await loadInitialData()
    } else {
      alert(res.data.error || '一键噬魂失败')
    }
  } catch (err) {
    alert('网络错误，请稍后重试')
    console.error('一键噬魂失败:', err)
  }
}

// 加载仓库魔魂数据
const loadWarehouseData = async () => {
  try {
    const params = new URLSearchParams()
    if (gradeFilter.value) params.append('grade', gradeFilter.value)
    params.append('page', page.value)
    params.append('pageSize', pageSize.value)
    
    const res = await http.get(`/mosoul/warehouse?${params.toString()}`)
    if (res.data.ok) {
      // 过滤掉目标魔魂本身（如果是从仓库进入的话）
      mosouls.value = (res.data.mosouls || []).filter(m => m.id != targetMosoulId.value)
      warehouseCount.value = res.data.warehouse_count || 0
      warehouseCapacity.value = res.data.warehouse_capacity || 90
      total.value = res.data.total || 0
      totalPages.value = res.data.totalPages || 1
    }
  } catch (err) {
    console.error('加载仓库数据失败:', err)
  }
}

onMounted(() => {
  loadInitialData()
})

// 筛选变化时重新加载
watch(gradeFilter, () => {
  page.value = 1
  loadWarehouseData()
})

// 切换品质筛选
const selectGrade = (grade) => {
  gradeFilter.value = grade
}

// 分页
const goPage = (p) => {
  if (p >= 1 && p <= totalPages.value) {
    page.value = p
    loadWarehouseData()
  }
}

// 摄魂操作（消耗材料升级目标）
const performAbsorb = async (materialMosoul) => {
  if (isMaxLevel.value) {
    alert('目标魔魂已满级，无法继续升级')
    return
  }
  
  const expProvide = getExpProvide(materialMosoul.grade)
  if (!confirm(`确定要消耗【${materialMosoul.name}】(提供${expProvide}经验)来升级【${targetMosoul.value.name}】吗？\n消耗后该魔魂将消失！`)) {
    return
  }
  
  try {
    const res = await http.post(`/mosoul/consume/${materialMosoul.id}`, {
      targetMosoulId: targetMosoulId.value
    })
    
    if (res.data.ok) {
      // 构建详细的成功消息
      let msg = res.data.message || '摄魂成功'
      if (res.data.levels_gained > 0) {
        msg += `\n等级: ${res.data.old_level} → ${res.data.new_level}`
      }
      if (res.data.is_max_level) {
        msg += '\n已达到满级！'
      }
      alert(msg)
      // 刷新数据
      await loadInitialData()
    } else {
      alert(res.data.error || '摄魂失败')
    }
  } catch (err) {
    alert('网络错误，请稍后重试')
    console.error('摄魂失败:', err)
  }
}

// 返回魔魂详情页
const goBack = () => {
  if (fromWarehouse.value) {
    router.push('/mosoul/warehouse')
  } else if (beastId.value) {
    router.push(`/beast/${beastId.value}/mosoul`)
  } else {
    router.push('/mosoul')
  }
}

// 返回首页
const goHome = () => {
  router.push('/')
}

// 获取品质颜色
const getGradeColor = (grade) => {
  const colors = {
    'god_soul': '#FFD700',
    'dragon_soul': '#9932CC',
    'heaven_soul': '#FF4500',
    'earth_soul': '#4169E1',
    'dark_soul': '#32CD32',
    'yellow_soul': '#808080',
    'waste_soul': '#A9A9A9',
  }
  return colors[grade] || '#000000'
}
</script>

<template>
  <div class="absorb-page">
    <div v-if="loading" class="section">加载中...</div>
    <div v-else-if="errorMsg" class="section error">{{ errorMsg }}</div>
    
      <template v-else>
        <!-- 目标魔魂信息 -->
        <div class="section title" v-if="targetMosoul">
          【升级对象：<span :style="{ color: getGradeColor(targetMosoul.grade) }">{{ targetMosoul.name }}</span>】
        </div>
        <div class="section" v-if="targetMosoul">
          品质: {{ targetMosoul.grade_name }} | 等级: {{ targetMosoul.level }}/10
        </div>
        <div class="section" v-if="targetMosoul && !isMaxLevel">
          经验: {{ targetMosoul.exp }}/{{ targetMosoul.max_exp || 2000 }}
        </div>
        <div class="section" v-if="isMaxLevel" style="color: #FF6600;">
          ★ 已满级 ★
        </div>
        
        <div class="separator"></div>
        
        <!-- 仓库筛选 -->
        <div class="section" v-if="!isMaxLevel">
          请选择要摄取的魔魂(黄魂+50 玄魂+100 地魂+200 天魂+400 龙魂+800 神魂+1000):
        </div>
        <div class="section" v-else style="color: #999;">
          魔魂已满级，无需继续升级
        </div>
      
      <!-- 品质筛选 -->
      <div class="section filter-row">
        <template v-for="(opt, index) in gradeOptions" :key="opt.value">
          <a 
            class="link filter-item"
            :class="{ active: gradeFilter === opt.value }"
            @click="selectGrade(opt.value)"
          >{{ opt.label }}</a>
          <span v-if="index < gradeOptions.length - 1">| </span>
        </template>
        <a v-if="!isMaxLevel" class="link" @click="performBatchAbsorb">一键噬魂</a>
      </div>
      
        <!-- 材料列表 -->
        <div v-for="(mosoul, index) in mosouls" :key="mosoul.id" class="section">
          {{ (page - 1) * pageSize + index + 1 }}. 
          <span :style="{ color: getGradeColor(mosoul.grade) }">{{ mosoul.name }}</span>({{ mosoul.grade_name }}) lv{{ mosoul.level }}
          <span class="exp-hint">[+{{ getExpProvide(mosoul.grade) }}经验]</span>
          <a v-if="!isMaxLevel" class="link" @click="performAbsorb(mosoul)">摄取</a>
        </div>
      
      <div v-if="mosouls.length === 0" class="section gray">
        没有可选的魔魂材料
      </div>
      
      <!-- 分页 -->
      <div v-if="totalPages > 1" class="section pagination">
        <a v-if="page < totalPages" class="link" @click="goPage(page + 1)">下页</a>
        <a v-if="page < totalPages" class="link" @click="goPage(totalPages)">末页</a>
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
.absorb-page {
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

.separator {
  height: 1px;
  background: #ffffffCCC;
  margin: 10px 0;
}

.filter-row {
  margin: 8px 0;
}

.filter-item {
  margin-right: 2px;
}

.filter-item.active {
  color: #FF6600;
  font-weight: bold;
}

.spacer {
  margin-top: 16px;
}

.link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: none;
  margin-right: 4px;
}

.link:hover {
  text-decoration: underline;
}

.pagination {
  margin-top: 8px;
}

.exp-hint {
  color: #999;
  font-size: 18px;
  margin-right: 4px;
}

.error {
  color: red;
}

.gray {
  color: #666;
}

.footer {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #CCCCCC;
}

.small {
  font-size: 17px;
}
</style>
