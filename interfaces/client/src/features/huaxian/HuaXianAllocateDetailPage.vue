<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()

// ========== 加载状态 ==========
const loading = ref(true)
const errorMsg = ref('')
const operating = ref(false)

// ========== 化仙池信息 ==========
const expPool = ref(0)
const expPoolMax = ref(0)

// ========== 幻兽信息 ==========
const beast = ref(null)

// ========== 分配数量 ==========
const allocateAmount = ref('')

// 最多可分配经验（取经验池余额）
const maxAllocate = computed(() => {
  return expPool.value
})

// ========== 加载数据 ==========
const loadData = async () => {
  loading.value = true
  errorMsg.value = ''
  
  const beastId = route.params.beastId
  if (!beastId) {
    errorMsg.value = '缺少幻兽ID'
    loading.value = false
    return
  }
  
  try {
    // 并行加载幻兽信息和化仙池状态
    const [beastRes, poolRes] = await Promise.all([
      http.get(`/beast/${beastId}`),
      http.get('/immortalize/status'),
    ])
    
    if (beastRes.data.ok) {
      beast.value = beastRes.data.beast
    } else {
      errorMsg.value = beastRes.data.error || '加载失败'
    }
    
    if (poolRes.data.ok) {
      expPool.value = poolRes.data.current_exp || 0
      expPoolMax.value = poolRes.data.capacity || 0
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
// 确定分配
const confirmAllocate = async () => {
  const amount = parseInt(allocateAmount.value)
  if (!amount || amount <= 0) {
    alert('请输入有效的分配数量')
    return
  }
  if (amount > maxAllocate.value) {
    alert(`最多只能分配${maxAllocate.value}点经验`)
    return
  }
  
  operating.value = true
  try {
    const res = await http.post('/beast/add-exp-from-pool', {
      beastId: beast.value.id,
      exp: amount
    })
    if (res.data.ok) {
      alert(res.data.message)
      // 重新加载数据
      await loadData()
      // 清空输入框
      allocateAmount.value = ''
    } else {
      alert(res.data.error || '分配失败')
    }
  } catch (err) {
    alert('网络错误，请稍后重试')
    console.error('分配经验失败:', err)
  } finally {
    operating.value = false
  }
}

// 全部分配
const allocateAll = () => {
  allocateAmount.value = maxAllocate.value.toString()
  confirmAllocate()
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
  <div class="allocate-detail-page">
    <!-- 加载状态 -->
    <div v-if="loading" class="section">加载中...</div>
    <div v-else-if="errorMsg" class="section" style="color: red;">{{ errorMsg }}</div>
    
    <template v-if="!loading && beast">
      <!-- 标题 -->
      <div class="section title">
        【化仙池经验分配】
      </div>
      
      <!-- 经验池 -->
      <div class="section">
        经验池：({{ expPool }}/{{ expPoolMax }})
      </div>
      
      <!-- 幻兽信息 -->
      <div class="section">
        <a class="link">{{ beast.name }}</a> ({{ beast.level }}级) 最多分配{{ maxAllocate }}点经验
      </div>
      
      <!-- 分配输入 -->
      <div class="section spacer">
        分配数量：<input type="text" v-model="allocateAmount" class="amount-input" />
        <button class="confirm-btn" @click="confirmAllocate">确定</button>
      </div>
      
      <!-- 全部分配 -->
      <div class="section spacer">
        <a class="link" @click="allocateAll">全部分配</a>
      </div>
    </template>

    <!-- 返回 -->
    <div class="section spacer">
      <a class="link" @click="goBack">返回化仙池</a>
    </div>
    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>

  </div>
</template>

<style scoped>
.allocate-detail-page {
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

.gray {
  color: #666666;
}

.small {
  font-size: 11px;
}

.amount-input {
  width: 180px;
  font-size: 12px;
  border: 1px solid #CCCCCC;
  padding: 2px 4px;
}

.confirm-btn {
  font-size: 12px;
  padding: 2px 12px;
  background: #F0F0F0;
  border: 1px solid #CCCCCC;
  cursor: pointer;
  margin-left: 8px;
}

.confirm-btn:hover {
  background: #E0E0E0;
}

.footer {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #CCCCCC;
}
</style>
