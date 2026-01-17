<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()

// 加载状态
const loading = ref(true)
const errorMsg = ref('')

// 幻兽和槽位信息
const beastId = ref(0)
const slotIndex = ref(0)

// 魔魂列表数据
const mosouls = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const totalPages = ref(1)

// 跳转页码输入
const jumpPageInput = ref(1)

// 展开的魔魂详情ID
const expandedMosoulId = ref(null)

// 切换魔魂详情展开状态
const toggleMosoulDetail = (mosoulId) => {
  if (expandedMosoulId.value === mosoulId) {
    expandedMosoulId.value = null
  } else {
    expandedMosoulId.value = mosoulId
  }
}

// 加载玩家魔魂列表
const loadMoSouls = async () => {
  loading.value = true
  errorMsg.value = ''
  
  try {
    const res = await http.get('/mosoul/player', {
      params: {
        page: currentPage.value,
        pageSize: pageSize.value,
        beast_id: beastId.value
      }
    })
    if (res.data.ok) {
      mosouls.value = res.data.mosouls || []
      total.value = res.data.total || 0
      totalPages.value = res.data.totalPages || 1
    } else {
      errorMsg.value = res.data.error || '加载失败'
    }
  } catch (err) {
    errorMsg.value = '网络错误，请稍后重试'
    console.error('加载魔魂列表失败:', err)
  } finally {
    loading.value = false
  }
}

// 使用魔魂（装备到幻兽）
const useMoSoul = async (mosoul) => {
  if (mosoul.beast_id) {
    console.error('该魔魂已装备在其他幻兽上，请先卸下')
    return
  }
  
  try {
    const res = await http.post(`/mosoul/equip/${mosoul.id}`, {
      beastId: beastId.value,
      slotIndex: slotIndex.value
    })
    if (res.data.ok) {
      console.error('装备成功')
      // 返回魔魂页面
      router.push(`/beast/${beastId.value}/mosoul`)
    } else {
      console.error(res.data.error || '装备失败')
    }
  } catch (err) {
    console.error('网络错误，请稍后重试')
    console.error('装备魔魂失败:', err)
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

// 分页操作
const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    loadMoSouls()
  }
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    loadMoSouls()
  }
}

const lastPage = () => {
  if (currentPage.value !== totalPages.value) {
    currentPage.value = totalPages.value
    loadMoSouls()
  }
}

const jumpToPage = () => {
  const page = parseInt(jumpPageInput.value)
  if (page >= 1 && page <= totalPages.value && page !== currentPage.value) {
    currentPage.value = page
    loadMoSouls()
  }
}

// 返回魔魂首页
const goBack = () => {
  router.push(`/beast/${beastId.value}/mosoul`)
}

// 返回首页
const goHome = () => {
  router.push('/')
}

onMounted(() => {
  beastId.value = parseInt(route.params.id)
  slotIndex.value = parseInt(route.query.slot) || 1
  jumpPageInput.value = 1
  loadMoSouls()
})
</script>

<template>
  <div class="mosoul-select-page">
    <!-- 加载状态 -->
    <div v-if="loading" class="section">加载中...</div>
    <div v-else-if="errorMsg" class="section error">{{ errorMsg }}</div>
    
    <!-- 魔魂列表 -->
    <template v-else>
      <div v-if="mosouls.length === 0" class="section">
        暂无魔魂
      </div>
      
      <template v-else>
        <!-- 魔魂列表 -->
        <div v-for="(mosoul, index) in mosouls" :key="mosoul.id" class="mosoul-item">
          <div class="section">
            {{ (currentPage - 1) * pageSize + index + 1 }}.<a 
              class="link" 
              :style="{ color: getGradeColor(mosoul.grade) }"
              @click="toggleMosoulDetail(mosoul.id)"
            >{{ mosoul.name }}({{ mosoul.grade_name }})</a> 
            lv{{ mosoul.level }} 
            <a 
              class="link" 
              @click="useMoSoul(mosoul)"
              :class="{ disabled: mosoul.beast_id }"
            >使用</a>
          </div>
          <!-- 魔魂属性详情 -->
          <div v-if="expandedMosoulId === mosoul.id" class="mosoul-detail">
            <div>lv{{ mosoul.level }} {{ mosoul.effect_text }}</div>
          </div>
        </div>
        
        <!-- 分页 -->
        <div class="section spacer-small">
          <a v-if="currentPage > 1" class="link" @click="prevPage">上页</a>
          <span v-else class="gray">上页</span>
          <span> </span>
          <a v-if="currentPage < totalPages" class="link" @click="nextPage">下页</a>
          <span v-else class="gray">下页</span>
          <span> </span>
          <a v-if="currentPage < totalPages" class="link" @click="lastPage">末页</a>
          <span v-else class="gray">末页</span>
        </div>
        
        <div class="section">
          {{ currentPage }}/{{ totalPages }}页 
          <input 
            type="text" 
            v-model="jumpPageInput" 
            class="page-input"
          />
          <button class="jump-btn" @click="jumpToPage">跳转</button>
        </div>
      </template>
      
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
.mosoul-select-page {
  background: #FFFFFF;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 16px;
  line-height: 1.6;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 2px 0;
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

.link.disabled {
  color: #999;
  cursor: not-allowed;
}

.gray {
  color: #666666;
}

.small {
  font-size: 17px;
}

.page-input {
  width: 40px;
  padding: 2px 4px;
  border: 1px solid #ccc;
  font-size: 18px;
}

.jump-btn {
  padding: 2px 8px;
  font-size: 18px;
  cursor: pointer;
  margin-left: 4px;
}

.mosoul-detail {
  padding-left: 20px;
  color: #228B22;
  margin: 2px 0;
}

.footer {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #CCCCCC;
}
</style>
