<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()

// 加载状态
const loading = ref(true)
const errorMsg = ref('')

// 储魂器数据
const warehouseCount = ref(0)
const warehouseCapacity = ref(90)

// 魔魂列表
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

// 加载数据
const loadData = async () => {
  loading.value = true
  errorMsg.value = ''
  
  try {
    const params = new URLSearchParams()
    if (gradeFilter.value) params.append('grade', gradeFilter.value)
    params.append('page', page.value)
    params.append('pageSize', pageSize.value)
    
    const res = await http.get(`/mosoul/warehouse?${params.toString()}`)
    if (res.data.ok) {
      mosouls.value = res.data.mosouls || []
      warehouseCount.value = res.data.warehouse_count || 0
      warehouseCapacity.value = res.data.warehouse_capacity || 90
      total.value = res.data.total || 0
      totalPages.value = res.data.totalPages || 1
    } else {
      errorMsg.value = res.data.error || '加载失败'
    }
  } catch (err) {
    errorMsg.value = '网络错误，请稍后重试'
    console.error('加载储魂器失败:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})

// 筛选变化时重新加载
watch(gradeFilter, () => {
  page.value = 1
  loadData()
})

// 切换品质筛选
const selectGrade = (grade) => {
  gradeFilter.value = grade
}

const getGradeLabel = (grade) => {
  const opt = gradeOptions.find(o => o.value === grade)
  return opt ? opt.label : grade
}

const performBatchAbsorbFromWarehouse = async () => {
  if (!mosouls.value || mosouls.value.length === 0) {
    alert('储魂器中没有魔魂')
    return
  }

  let target = null
  if (mosouls.value.length === 1) {
    target = mosouls.value[0]
  } else {
    const input = prompt(`请输入要升级的目标序号（当前页 1-${mosouls.value.length}）`, '1')
    if (input === null) return
    const idx = parseInt(input)
    if (!idx || idx < 1 || idx > mosouls.value.length) {
      alert('序号无效')
      return
    }
    target = mosouls.value[idx - 1]
  }

  const gradeText = '全部'
  if (!confirm(`确定要一键噬魂吗？\n\n升级对象：${target.name}\n材料品质：${gradeText}\n\n注意：将消耗储魂器内所有魔魂材料（不含升级对象），材料魔魂会消失！\n目标满级后，剩余材料仍会被吞噬（经验会浪费）。`)) {
    return
  }

  try {
    const res = await http.post('/mosoul/consume/batch', {
      targetMosoulId: target.id,
      grade: '',
    })

    if (res.data.ok) {
      alert(res.data.message || '一键噬魂成功')
      await loadData()
    } else {
      alert(res.data.error || '一键噬魂失败')
    }
  } catch (err) {
    alert('网络错误，请稍后重试')
    console.error('一键噬魂失败:', err)
  }
}

// 分页
const goPage = (p) => {
  if (p >= 1 && p <= totalPages.value) {
    page.value = p
    loadData()
  }
}

const jumpPage = () => {
  const p = parseInt(jumpPageInput.value)
  if (p >= 1 && p <= totalPages.value) {
    page.value = p
    loadData()
  }
}

const jumpPageInput = ref(1)

// 锁定魔魂
const lockMoSoul = (mosoul) => {
  alert(`锁定【${mosoul.name}】功能待实现`)
}

// 查看魔魂详情
const viewMoSoulDetail = (mosoul) => {
  router.push(`/mosoul/${mosoul.id}?from=warehouse`)
}

// 噬魂 - 跳转到摄魂页面
const consumeMoSoul = (mosoul) => {
  router.push(`/mosoul/${mosoul.id}/absorb?from=warehouse`)
}

// 猎魂
const goHunting = () => {
  alert('猎魂功能待实现')
}

// 返回魔魂首页
const goBack = () => {
  router.push('/mosoul')
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
  <div class="warehouse-page">
    <!-- 储魂器信息 -->
    <div class="section">
      储魂器： {{ warehouseCount }}/{{ warehouseCapacity }}
      <a class="link" @click="performBatchAbsorbFromWarehouse">一键噬魂</a>
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
    </div>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="section">加载中...</div>
    <div v-else-if="errorMsg" class="section error">{{ errorMsg }}</div>
    
    <template v-else>
        <!-- 魔魂列表 -->
        <div v-for="(mosoul, index) in mosouls" :key="mosoul.id" class="section">
          {{ (page - 1) * pageSize + index + 1 }}. 
          <a class="link" :style="{ color: getGradeColor(mosoul.grade) }" @click="viewMoSoulDetail(mosoul)">{{ mosoul.name }}</a>({{ mosoul.grade_name }}) lv{{ mosoul.level }}
          <a class="link" @click="lockMoSoul(mosoul)">锁定</a>
          <a class="link" @click="consumeMoSoul(mosoul)">噬魂</a>
        </div>
      
      <!-- 无数据提示 -->
      <div v-if="mosouls.length === 0" class="section gray">
        储魂器中没有魔魂
      </div>
      
      <!-- 分页 -->
      <div v-if="totalPages > 1" class="section pagination">
        <a v-if="page < totalPages" class="link" @click="goPage(page + 1)">下页</a>
        <a v-if="page < totalPages" class="link" @click="goPage(totalPages)">末页</a>
      </div>
      <div v-if="totalPages > 1" class="section">
        {{ page }}/{{ totalPages }}页
        <input type="number" v-model="jumpPageInput" class="page-input" min="1" :max="totalPages" />
        <button @click="jumpPage" class="jump-btn">跳转</button>
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

.page-input {
  width: 50px;
  margin: 0 4px;
  padding: 2px 4px;
}

.jump-btn {
  padding: 2px 8px;
  cursor: pointer;
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
