<script setup>
import { ref, onMounted } from 'vue'
import http from '@/services/http'
import { uiConfirm } from '@/stores/uiOverlayStore'

const isOpen = ref(false)
const isMinimized = ref(true)
const loading = ref(false)
const status = ref({})
const message = ref('')

// 表单数据
const vipLevel = ref(0)
const diamondSpent = ref(0)
const playerLevel = ref(1)
const playerExp = ref(0)
const addYuanbao = ref(1000)
const addCopper = ref(10000)
const addDiamond = ref(100)
const itemId = ref(6001)
const itemQuantity = ref(10)

// 拖拽相关
const panelRef = ref(null)
const position = ref({ x: 10, y: 10 })
const isDragging = ref(false)
const dragOffset = ref({ x: 0, y: 0 })

const togglePanel = () => {
  isMinimized.value = !isMinimized.value
  if (!isMinimized.value) {
    loadStatus()
  }
}

const loadStatus = async () => {
  loading.value = true
  try {
    const res = await http.get('/vip-test/status')
    if (res.data?.ok) {
      status.value = res.data
      vipLevel.value = res.data.vip_level || 0
      diamondSpent.value = res.data.diamond_spent || 0
    }
  } catch (e) {
    message.value = '加载失败: ' + e.message
  } finally {
    loading.value = false
  }
}

const setVip = async () => {
  try {
    const res = await http.post('/vip-test/set-vip', {
      vip_level: parseInt(vipLevel.value),
      diamond_spent: parseInt(diamondSpent.value)
    })
    message.value = res.data?.message || '设置成功'
    loadStatus()
  } catch (e) {
    message.value = '设置失败: ' + e.message
  }
}

const setLevel = async () => {
  try {
    const res = await http.post('/vip-test/set-level', {
      level: parseInt(playerLevel.value),
      exp: parseInt(playerExp.value)
    })
    message.value = res.data?.message || '设置成功'
    loadStatus()
  } catch (e) {
    message.value = '设置失败: ' + e.message
  }
}

const syncVipLevel = async () => {
  try {
    // 只传消耗宝石数，让后端自动计算等级
    const res = await http.post('/vip-test/set-vip', {
      vip_level: 0,
      diamond_spent: status.value.diamond_spent
    })
    message.value = res.data?.message || '同步成功'
    loadStatus()
  } catch (e) {
    message.value = '同步失败: ' + e.message
  }
}

const resetDaily = async () => {
  try {
    const res = await http.post('/vip-test/reset-daily')
    message.value = res.data?.message || '重置成功'
    loadStatus()
  } catch (e) {
    message.value = '重置失败: ' + e.message
  }
}

const resetGifts = async () => {
  try {
    const res = await http.post('/vip-test/reset-gifts')
    message.value = res.data?.message || '重置成功'
    loadStatus()
  } catch (e) {
    message.value = '重置失败: ' + e.message
  }
}

const resetPlayer = async () => {
  if (!(await uiConfirm('确定要重置玩家所有数据吗？'))) return
  try {
    const res = await http.post('/vip-test/reset-player')
    message.value = res.data?.message || '重置成功'
    loadStatus()
  } catch (e) {
    message.value = '重置失败: ' + e.message
  }
}

const mockRecharge = async (productId) => {
  try {
    const res = await http.post('/vip-test/mock-recharge', { product_id: productId })
    message.value = res.data?.message || '充值成功'
    loadStatus()
  } catch (e) {
    message.value = '充值失败: ' + e.message
  }
}

const skipDay = async () => {
  try {
    const res = await http.post('/vip-test/skip-day')
    message.value = res.data?.message || '已跳转第二天'
    loadStatus()
  } catch (e) {
    message.value = '跳转失败: ' + e.message
  }
}

const batchMonthCard = async (count) => {
  try {
    const res = await http.post('/vip-test/batch-month-card', { count })
    message.value = res.data?.message || '购买成功'
    loadStatus()
  } catch (e) {
    message.value = '购买失败: ' + e.message
  }
}

const addCurrency = async () => {
  try {
    const res = await http.post('/vip-test/add-currency', {
      yuanbao: parseInt(addYuanbao.value) || 0,
      copper: parseInt(addCopper.value) || 0,
      diamond: parseInt(addDiamond.value) || 0
    })
    message.value = res.data?.message || '添加成功'
    loadStatus()
  } catch (e) {
    message.value = '添加失败: ' + e.message
  }
}

const addItem = async () => {
  try {
    const res = await http.post('/vip-test/add-item', {
      item_id: parseInt(itemId.value),
      quantity: parseInt(itemQuantity.value)
    })
    message.value = res.data?.message || '添加成功'
  } catch (e) {
    message.value = '添加失败: ' + e.message
  }
}

// 拖拽功能
const startDrag = (e) => {
  isDragging.value = true
  dragOffset.value = {
    x: e.clientX - position.value.x,
    y: e.clientY - position.value.y
  }
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)
}

const onDrag = (e) => {
  if (!isDragging.value) return
  position.value = {
    x: e.clientX - dragOffset.value.x,
    y: e.clientY - dragOffset.value.y
  }
}

const stopDrag = () => {
  isDragging.value = false
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
}

onMounted(() => {
  // 从右下角开始
  position.value = { x: window.innerWidth - 320, y: 10 }
})
</script>

<template>
  <div 
    class="debug-panel" 
    ref="panelRef"
    :style="{ left: position.x + 'px', top: position.y + 'px' }"
  >
    <!-- 标题栏 -->
    <div class="panel-header" @mousedown="startDrag">
      <span>🔧 调试面板</span>
      <button class="toggle-btn" @click.stop="togglePanel">
        {{ isMinimized ? '展开' : '收起' }}
      </button>
    </div>
    
    <!-- 内容区 -->
    <div v-show="!isMinimized" class="panel-body">
      <div v-if="message" class="msg">{{ message }}</div>
      
      <div class="section-title">当前状态</div>
      <div v-if="loading">加载中...</div>
      <template v-else>
        <div style="color:#f60;font-weight:bold">📅 游戏日期: {{ status.game_date }} (跳过{{ status.skip_days || 0 }}天)</div>
        <div>Lv{{ status.level }} | 经验{{ status.exp }}</div>
        <div>VIP{{ status.vip_level }} | 消耗宝石{{ status.diamond_spent }}</div>
        <div>元宝{{ status.yuanbao }} | 铜币{{ status.copper }} | 宝石{{ status.diamond }}</div>
      </template>
      
      <div class="section-title">设置等级</div>
      <div class="btn-row">
        <a class="link" @click="playerLevel=1;playerExp=0;setLevel()">Lv1</a>
        <a class="link" @click="playerLevel=10;playerExp=0;setLevel()">Lv10</a>
        <a class="link" @click="playerLevel=20;playerExp=0;setLevel()">Lv20</a>
        <a class="link" @click="playerLevel=50;playerExp=0;setLevel()">Lv50</a>
        <a class="link" @click="playerLevel=100;playerExp=0;setLevel()">Lv100</a>
      </div>
      
      <div class="section-title">快捷VIP</div>
      <div class="btn-row">
        <a class="link" @click="vipLevel=0;diamondSpent=0;setVip()">V0</a>
        <a class="link" @click="vipLevel=1;diamondSpent=1;setVip()">V1</a>
        <a class="link" @click="vipLevel=3;diamondSpent=100;setVip()">V3</a>
        <a class="link" @click="vipLevel=5;diamondSpent=500;setVip()">V5</a>
        <a class="link" @click="vipLevel=10;diamondSpent=20000;setVip()">V10</a>
      </div>
      
      <div class="section-title">重置</div>
      <div class="btn-row">
        <a class="link" @click="resetDaily">每日</a>
        <a class="link" @click="resetGifts">礼包</a>
        <a class="link danger" @click="resetPlayer">全部</a>
        <a class="link" style="color:#09f" @click="skipDay">跳转第二天</a>
      </div>
      
      <div class="section-title">批量月卡</div>
      <div class="btn-row">
        <a class="link" @click="batchMonthCard(1)">1张</a>
        <a class="link" @click="batchMonthCard(3)">3张</a>
        <a class="link" @click="batchMonthCard(10)">10张</a>
        <a class="link" @click="batchMonthCard(20)">20张</a>
        <a class="link" @click="batchMonthCard(50)">50张</a>
      </div>
      
      <div class="section-title">模拟充值</div>
      <div class="btn-row">
        <a class="link" @click="mockRecharge('diamond_10')">10宝石</a>
        <a class="link" @click="mockRecharge('diamond_30')">30宝石</a>
        <a class="link" @click="mockRecharge('diamond_50')">50宝石</a>
        <a class="link" @click="mockRecharge('diamond_100')">100宝石</a>
      </div>
      <div class="btn-row">
        <a class="link" style="color:#f60" @click="mockRecharge('diamond_300')">300宝石(首充双倍)</a>
        <a class="link" style="color:#f60" @click="mockRecharge('diamond_500')">500宝石(首充双倍)</a>
      </div>
      
      <div class="section-title">添加货币</div>
      <div class="input-row">
        <input type="number" v-model="addYuanbao" placeholder="元宝" />
        <input type="number" v-model="addCopper" placeholder="铜币" />
        <a class="link" @click="addCurrency">添加</a>
      </div>
      
      <div class="section-title">添加物品</div>
      <div class="input-row">
        <input type="number" v-model="itemId" placeholder="物品ID" />
        <input type="number" v-model="itemQuantity" placeholder="数量" />
        <a class="link" @click="addItem">添加</a>
      </div>
      <div class="hint">6001化仙丹 6002骰子包 6018传送符</div>
    </div>
  </div>
</template>

<style scoped>
.debug-panel {
  position: fixed;
  z-index: 9999;
  background: #fffef0;
  border: 2px solid #8b4513;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
  min-width: 280px;
  font-size: 18px;
  font-family: 'SimSun', serif;
}

.panel-header {
  background: #8b4513;
  color: #fff;
  padding: 6px 10px;
  cursor: move;
  display: flex;
  justify-content: space-between;
  align-items: center;
  user-select: none;
}

.toggle-btn {
  background: #fff;
  color: #8b4513;
  border: none;
  padding: 2px 8px;
  cursor: pointer;
  font-size: 17px;
}

.panel-body {
  padding: 8px 10px;
  max-height: 400px;
  overflow-y: auto;
}

.section-title {
  font-weight: bold;
  color: #8b4513;
  margin: 8px 0 4px;
  border-bottom: 1px dashed #ccc;
}

.msg {
  color: #006600;
  background: #e6ffe6;
  padding: 2px 6px;
  margin-bottom: 6px;
}

.btn-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.input-row {
  display: flex;
  gap: 4px;
  align-items: center;
}

.input-row input {
  width: 60px;
  padding: 2px 4px;
}

.link {
  color: #0066cc;
  cursor: pointer;
}
.link:hover { text-decoration: underline; }
.link.danger { color: #cc0000; }

.hint {
  font-size: 10px;
  color: #888;
  margin-top: 4px;
}
</style>
