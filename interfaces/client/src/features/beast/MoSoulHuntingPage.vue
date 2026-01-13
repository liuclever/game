<script setup>
import { useMessage } from '@/composables/useMessage'
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()

// 加载状态
const { message, messageType, showMessage } = useMessage()

const loading = ref(true)
const errorMsg = ref('')

// 场次类型
const arenaType = ref('normal')

// 猎魂师列表
const hunters = ref([])

// 玩家铜钱
const gold = ref(0)

// 追魂法宝数量（高级场消耗）
const soulCharm = ref(0)

// 一键猎魂状态
const batchHunting = ref(false)
const batchResults = ref(null)

// 加载数据
const loadData = async () => {
  loading.value = true
  errorMsg.value = ''
  
  try {
    const res = await http.get(`/mosoul/hunting?arena=${arenaType.value}`)
    if (res.data.ok) {
      hunters.value = res.data.hunters || []
      gold.value = res.data.gold || 0
      soulCharm.value = res.data.soul_charm || 0
    } else {
      errorMsg.value = res.data.error || '加载失败'
    }
  } catch (err) {
    errorMsg.value = '网络错误，请稍后重试'
    console.error('加载猎魂页面失败:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})

// 切换场次时重新加载
watch(arenaType, () => {
  loadData()
})

// 切换场次
const selectArena = (type) => {
  arenaType.value = type
}

// 获取费用显示文本
const getCostText = (hunter) => {
  if (hunter.cost_type === 'fabao') {
    return `${hunter.cost}追魂法宝`
  }
  return `${hunter.cost}铜钱`
}

// 执行猎魂
const doHunting = async (hunter) => {
  if (!hunter.available) {
    showMessage(`${hunter.name}尚未解锁`, 'info')
    return
  }

  if (hunter.cost_type === 'fabao') {
    if (soulCharm.value < hunter.cost) {
      showMessage('追魂法宝不足', 'error')
      return
    }
  } else {
    if (gold.value < hunter.cost) {
      showMessage('铜钱不足', 'error')
      return
    }
  }
  
  const costText = getCostText(hunter)
  // 已移除确认提示
  
  try {
    const res = await http.post('/mosoul/hunting/hunt', {
      hunterId: hunter.id,
      arenaType: arenaType.value,
    })
    if (res.data.ok) {
      let msg = res.data.message
      // 如果解锁了下一个猎魂师，提示
      if (res.data.next_unlocked && res.data.next_hunter) {
        const nextName = getHunterName(res.data.next_hunter)
        msg += `\n遍到了${nextName}！`
      }
      showMessage(msg, 'info')
      gold.value = res.data.remaining_gold
      // 重新加载更新解锁状态
      await loadData()
    } else {
      showMessage(res.data.error || '猎魂失败', 'error')
    }
  } catch (err) {
    showMessage('网络错误，请稍后重试', 'error')
    console.error('猎魂失败:', err)
  }
}

// 获取猎魂师名称
const getHunterName = (hunterId) => {
  const names = {
    'amy': '艾米',
    'keke': '科科',
    'boer': '波尔',
    'wote': '沃特',
    'kaiwen': '凯文',
  }
  return names[hunterId] || hunterId
}

// 一键猎魂
const doOneKeyHunting = async () => {
  if (arenaType.value === 'advanced') {
    const minCharm = hunters.value.reduce((min, h) => {
      const cost = h.cost_type === 'fabao' ? h.cost : Infinity
      return h.available && cost < min ? cost : min
    }, Infinity)

    if (soulCharm.value < minCharm) {
      showMessage('追魂法宝不足，无法进行一键猎魂', 'error')
      return
    }
  } else {
    // 获取当前最低费用
    const minCost = hunters.value.reduce((min, h) => {
      const cost = h.cost
      return h.available && cost < min ? cost : min
    }, Infinity)

    if (gold.value < minCost) {
      showMessage('铜钱不足，无法进行一键猎魂', 'error')
      return
    }
  }
  
  // 已移除确认提示
  
  batchHunting.value = true
  batchResults.value = null
  
  try {
    const res = await http.post('/mosoul/hunting/batch-hunt', {
      arenaType: arenaType.value,
    })
    if (res.data.ok) {
      batchResults.value = res.data
      gold.value = res.data.remaining_gold
      await loadData()
    } else {
      showMessage(res.data.error || '一键猎魂失败', 'error')
    }
  } catch (err) {
    showMessage('网络错误，请稍后重试', 'error')
    console.error('一键猎魂失败:', err)
  } finally {
    batchHunting.value = false
  }
}

// 关闭结果弹窗
const closeBatchResults = () => {
  batchResults.value = null
}

// 返回魔魂首页
const goBack = () => {
  router.push('/mosoul')
}

// 返回首页
const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="hunting-page">
    <!-- 消息提示 -->
    <div v-if="message" class="message" :class="messageType">
      {{ message }}
    </div>

    <!-- 标题 -->
    <div class="section title-section">
      【魔魂-猎魂】 <a class="link" @click="() => window.showMessage('猎魂简介：花费铜钱让猎魂师帮你捕捉魔魂，不同猎魂师获得高品质魔魂的概率不同。', 'success')">简介</a>
    </div>
    
    <!-- 场次选择 -->
    <div class="section">
      <a 
        class="link arena-item"
        :class="{ active: arenaType === 'normal' }"
        @click="selectArena('normal')"
      >普通场</a>| 
      <a 
        class="link arena-item"
        :class="{ active: arenaType === 'advanced' }"
        @click="selectArena('advanced')"
      >高级场</a>
    </div>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="section">加载中...</div>
    <div v-else-if="errorMsg" class="section error">{{ errorMsg }}</div>
    
    <template v-else>
      <!-- 猎魂师选择提示 -->
      <div class="section">
        请选择猎魂师:
      </div>
      
      <!-- 猎魂师列表 -->
      <div class="section hunter-list">
        <template v-for="(hunter, index) in hunters" :key="hunter.id">
          <a 
            class="link hunter-name" 
            :class="{ disabled: !hunter.available, available: hunter.available }"
            @click="doHunting(hunter)"
          >{{ hunter.name }}</a>
          <span v-if="index < hunters.length - 1">→ </span>
        </template>
      </div>
      
      <!-- 猎魂费用标题 -->
      <div class="section">
        [猎魂费用]
      </div>
      
<!-- 一键猎魂 -->
        <div class="section">
          <a class="link" :class="{ disabled: batchHunting }" @click="doOneKeyHunting">
            {{ batchHunting ? '猎魂中...' : '一键猎魂' }}
          </a>
        </div>
      
      <!-- 费用列表 -->
      <div v-for="hunter in hunters" :key="'cost-' + hunter.id" class="section">
        {{ hunter.name }}：{{ getCostText(hunter) }}
      </div>
      
      <!-- 玩家铜钱 -->
      <div class="section" v-if="arenaType === 'normal'">
        铜钱：{{ gold }}
      </div>
      <div class="section" v-else>
        追魂法宝：{{ soulCharm }}
      </div>
      
      <!-- 导航 -->
      <div class="section spacer">
        <a class="link" @click="goBack">返回魔魂首页</a>
      </div>
      <div class="section">
        <a class="link" @click="goHome">返回游戏首页</a>
      </div>
    </template>
    
    
    <!-- 一键猎魂结果弹窗 -->
    <div v-if="batchResults" class="modal-overlay" @click.self="closeBatchResults">
      <div class="modal-content">
        <div class="modal-header">
          【一键猎魂结果】
          <a class="link close-btn" @click="closeBatchResults">关闭</a>
        </div>
        
        <div class="modal-body">
          <!-- 统计信息 -->
          <div class="summary-section">
            <div>猎魂次数：{{ batchResults.summary.total_hunts }}次</div>
            <template v-if="batchResults.summary.cost_type === 'soul_charm'">
              <div>总花费：{{ batchResults.summary.total_cost }}追魂法宝</div>
              <div>净花费：{{ batchResults.summary.net_cost }}追魂法宝</div>
            </template>
            <template v-else>
              <div>总花费：{{ batchResults.summary.total_cost }}铜钱</div>
              <div v-if="batchResults.summary.total_sell > 0">废魂售卖：+{{ batchResults.summary.total_sell }}铜钱</div>
              <div>净花费：{{ batchResults.summary.net_cost }}铜钱</div>
            </template>
            <div>获得魔魂：{{ batchResults.summary.obtained_count }}个</div>
          </div>
          
          <!-- 品质统计 -->
          <div v-if="Object.keys(batchResults.summary.grade_summary).length > 0" class="grade-summary">
            <div class="grade-title">[获得魔魂品质]</div>
            <div v-for="(count, grade) in batchResults.summary.grade_summary" :key="grade">
              {{ grade }}：{{ count }}个
            </div>
          </div>
          
          <!-- 详细结果 -->
          <div class="results-list">
            <div class="results-title">[详细记录]</div>
            <div v-for="result in batchResults.results" :key="result.hunt_num" class="result-item">
              <template v-if="result.stopped">
                <span class="stopped">第{{ result.hunt_num }}次：{{ result.reason }}，停止猎魂</span>
              </template>
              <template v-else>
                <span>第{{ result.hunt_num }}次({{ result.hunter }})：</span>
                <span v-if="result.is_waste" class="waste">废魂(+{{ result.sell_price }})</span>
                <span v-else :class="'grade-' + result.mosoul?.grade">{{ result.mosoul?.name }}</span>
                <span v-if="result.next_unlocked" class="unlock"> 遇到{{ getHunterName(result.next_hunter) }}！</span>
              </template>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.hunting-page {
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

.title-section {
  font-weight: bold;
}

.arena-item {
  margin-right: 2px;
}

.arena-item.active {
  color: #FF6600;
  font-weight: bold;
}

.hunter-list {
  margin: 8px 0;
}

.hunter-name {
  margin-right: 2px;
}

.hunter-name.available {
  color: #0066CC;
}

.hunter-name.disabled {
  color: #999;
  cursor: not-allowed;
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

.gray {
  color: #666;
}

.footer {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #CCCCCC;
}

.small {
  font-size: 11px;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: #FFF8DC;
  border: 2px solid #8B4513;
  max-width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  padding: 12px;
}

.modal-header {
  font-weight: bold;
  margin-bottom: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.close-btn {
  font-weight: normal;
}

.modal-body {
  font-size: 12px;
}

.summary-section {
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px dashed #999;
}

.grade-summary {
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px dashed #999;
}

.grade-title,
.results-title {
  font-weight: bold;
  margin-bottom: 4px;
}

.results-list {
  max-height: 200px;
  overflow-y: auto;
}

.result-item {
  margin: 2px 0;
}

.waste {
  color: #999;
}

.stopped {
  color: #CC0000;
}

.unlock {
  color: #FF6600;
  font-weight: bold;
}

/* 品质颜色 */
.grade-yellow_soul {
  color: #B8860B;
}

.grade-dark_soul {
  color: #4B0082;
}

.grade-earth_soul {
  color: #8B4513;
}

.grade-heaven_soul {
  color: #0066CC;
}

.grade-dragon_soul {
  color: #FF6600;
}

.grade-god_soul {
  color: #FF0000;
}

.link.disabled {
  color: #999;
  cursor: not-allowed;
}

/* 消息提示样式 */
.message {
  padding: 12px;
  margin: 12px 0;
  border-radius: 4px;
  font-weight: bold;
  text-align: center;
}

.message.success {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.message.error {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.message.info {
  background: #d1ecf1;
  color: #0c5460;
  border: 1px solid #bee5eb;
}

</style>
