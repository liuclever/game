<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const loading = ref(true)
const errorMsg = ref('')
const info = ref(null)
const refreshing = ref(false)
const submittingDeposit = ref(false)

const depositDialog = reactive({
  visible: false,
  item: null,
  quantity: 1,
})

const fetchStorageInfo = async () => {
  loading.value = true
  errorMsg.value = ''
  try {
    const res = await http.get('/alliance/item-storage')
    if (res.data?.ok) {
      info.value = res.data
    } else {
      errorMsg.value = res.data?.error || '获取寄存仓库信息失败'
    }
  } catch (err) {
    console.error('load storage failed', err)
    errorMsg.value = err.response?.data?.error || '网络异常，请稍后再试'
  } finally {
    loading.value = false
  }
}

const refresh = async () => {
  refreshing.value = true
  await fetchStorageInfo()
  refreshing.value = false
}

onMounted(fetchStorageInfo)

const allianceName = computed(() => info.value?.alliance?.name || '')
const bagInfo = computed(() => info.value?.bag || null)
const inventoryItems = computed(() => info.value?.inventory || [])
const storageItems = computed(() => info.value?.storage?.items || [])
const ownStorageItems = computed(() => info.value?.storage?.ownItems || [])
const storageCapacity = computed(() => {
  const storage = info.value?.storage
  if (!storage) return { used: 0, capacity: 0, percent: 0 }
  const used = storage.used || 0
  const capacity = storage.capacity || 0
  const percent = capacity > 0 ? Math.min(100, Math.round((used / capacity) * 100)) : 0
  return { used, capacity, percent }
})

const openDepositDialog = (item) => {
  depositDialog.item = item
  depositDialog.quantity = 1
  depositDialog.visible = true
}

const closeDepositDialog = () => {
  depositDialog.visible = false
  depositDialog.item = null
  depositDialog.quantity = 1
}

const submitDeposit = async () => {
  if (!depositDialog.item) return
  const quantity = Number(depositDialog.quantity)
  if (!Number.isInteger(quantity) || quantity <= 0) {
    alert('请输入正确的寄存数量')
    return
  }
  if (quantity > depositDialog.item.quantity) {
    alert('寄存数量不能超过背包拥有数量')
    return
  }
  submittingDeposit.value = true
  try {
    const res = await http.post('/alliance/item-storage/deposit', {
      itemId: depositDialog.item.itemId,
      quantity,
    })
    if (res.data?.ok) {
      info.value = res.data.snapshot
      alert('寄存成功')
      closeDepositDialog()
    } else {
      alert(res.data?.error || '寄存失败')
    }
  } catch (err) {
    console.error('deposit failed', err)
    alert(err.response?.data?.error || '寄存失败，请稍后再试')
  } finally {
    submittingDeposit.value = false
  }
}

const pendingWithdraw = () => {
  alert('取回功能即将上线，敬请期待')
}

const goAlliance = () => router.push('/alliance')
const goWarehouse = () => router.push('/alliance/warehouse')
</script>

<template>
  <div class="storage-page">
    <div class="hero">
      <div class="hero-content">
        <div class="eyebrow">联盟寄存仓库</div>
        <h1>{{ allianceName || '未加入联盟' }}</h1>
        <p v-if="bagInfo">
          当前背包：{{ bagInfo.bag_name }} ｜ 容量 {{ bagInfo.used_slots }}/{{ bagInfo.capacity }}
        </p>
        <div class="hero-actions">
          <button class="btn ghost" @click="goAlliance">返回联盟</button>
          <button class="btn ghost" @click="goWarehouse">查看物资库</button>
          <button class="btn ghost" :disabled="refreshing" @click="refresh">
            {{ refreshing ? '刷新中...' : '刷新数据' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="section">加载中...</div>
    <div v-else-if="errorMsg" class="section error">{{ errorMsg }}</div>
    <template v-else-if="info">
      <div class="section capacity-card">
        <div class="capacity-title">仓库容量</div>
        <div class="capacity-values">
          <strong>{{ storageCapacity.used }}</strong>
          <span>/ {{ storageCapacity.capacity }} 格</span>
        </div>
        <div class="capacity-bar">
          <div class="capacity-bar-fill" :style="{ width: storageCapacity.percent + '%' }" />
        </div>
        <div class="capacity-tip">
          每级联盟 +5 格 ｜ 当前占用 {{ storageCapacity.percent }}%
        </div>
      </div>

      <div class="section inventory-section">
        <div class="section-header">
          <h2>背包物品</h2>
          <span class="sub">可选择寄存的物品（单种最多 99 个 / 格）</span>
        </div>
        <div v-if="inventoryItems.length" class="inventory-grid">
          <div v-for="item in inventoryItems" :key="item.itemId" class="inventory-card">
            <div class="item-headline">
              <strong>{{ item.name }}</strong>
              <span class="tag">{{ item.type }}</span>
            </div>
            <p class="desc">{{ item.description || '暂无描述' }}</p>
            <div class="meta-row">
              <span>拥有：{{ item.quantity }}</span>
              <span>可堆叠：{{ item.stackable ? '是' : '否' }}</span>
            </div>
            <button class="btn primary small" @click="openDepositDialog(item)">寄存</button>
          </div>
        </div>
        <div v-else class="empty">背包暂无可寄存物品</div>
      </div>

      <div class="section storage-section">
        <div class="section-header">
          <h2>仓库物品</h2>
          <span class="sub">按时间先后排列，优先展示自己的寄存</span>
        </div>
        <div v-if="storageItems.length" class="storage-table">
          <div class="storage-row storage-header">
            <span>物品</span>
            <span>数量</span>
            <span>所属</span>
            <span>寄存时间</span>
            <span>操作</span>
          </div>
          <div v-for="record in storageItems" :key="record.storageId" class="storage-row">
            <span>
              <strong>{{ record.name }}</strong>
              <small>#{{ record.itemId }}</small>
            </span>
            <span>{{ record.quantity }}</span>
            <span>
              <span v-if="record.ownerIsSelf" class="badge">我</span>
              <span v-else>成员 {{ record.ownerUserId }}</span>
            </span>
            <span>{{ record.storedAt || '-' }}</span>
            <span>
              <button
                class="btn outline tiny"
                :disabled="!record.ownerIsSelf"
                @click="pendingWithdraw"
              >
                {{ record.ownerIsSelf ? '取回(预留)' : '仅限本人' }}
              </button>
            </span>
          </div>
        </div>
        <div v-else class="empty">仓库暂空，快来寄存珍贵物资吧！</div>
      </div>

      <div class="section own-section" v-if="ownStorageItems.length">
        <div class="section-header">
          <h2>我的寄存</h2>
          <span class="sub">仅显示个人寄存记录，方便管理</span>
        </div>
        <div class="own-grid">
          <div v-for="record in ownStorageItems" :key="record.storageId" class="own-card">
            <div class="item-headline">
              <strong>{{ record.name }}</strong>
              <small>#{{ record.itemId }}</small>
            </div>
            <p>数量：{{ record.quantity }}</p>
            <p>寄存时间：{{ record.storedAt || '-' }}</p>
            <button class="btn outline small" @click="pendingWithdraw">取回（预留）</button>
          </div>
        </div>
      </div>
    </template>
    <div v-else class="section">
      尚未加入联盟，无法使用寄存仓库
    </div>

    <div v-if="depositDialog.visible" class="dialog-backdrop" @click.self="closeDepositDialog">
      <div class="dialog">
        <h3>寄存 {{ depositDialog.item?.name }}</h3>
        <p class="dialog-tip">
          本次最多可寄存 {{ depositDialog.item?.quantity }} 个，将直接扣除背包物品。
        </p>
        <label>
          寄存数量：
          <input
            type="number"
            min="1"
            :max="depositDialog.item?.quantity"
            v-model.number="depositDialog.quantity"
          />
        </label>
        <div class="dialog-actions">
          <button class="btn ghost" @click="closeDepositDialog">取消</button>
          <button class="btn primary" :disabled="submittingDeposit" @click="submitDeposit">
            {{ submittingDeposit ? '寄存中...' : '确认寄存' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.storage-page {
  min-height: 100vh;
  background: radial-gradient(circle at top, #fef5e7, #f9e5c8 45%, #f4d9b4);
  padding-bottom: 40px;
  color: #4a2b0b;
  font-family: 'Noto Serif SC', '宋体', serif;
}

.hero {
  background: linear-gradient(120deg, #5c3315, #8a5522);
  color: #fff3dd;
  padding: 32px 20px;
  text-align: center;
  clip-path: polygon(0 0, 100% 0, 100% 85%, 50% 100%, 0 85%);
}

.hero-content h1 {
  font-size: 28px;
  margin: 4px 0;
}

.hero-actions {
  margin-top: 16px;
  display: flex;
  justify-content: center;
  gap: 10px;
  flex-wrap: wrap;
}

.eyebrow {
  letter-spacing: 6px;
  text-transform: uppercase;
  font-size: 12px;
  opacity: 0.8;
}

.section {
  margin: 20px auto;
  width: min(960px, 92vw);
  background: rgba(255, 255, 255, 0.9);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 6px 18px rgba(90, 56, 18, 0.15);
}

.capacity-card {
  border: 1px solid rgba(92, 51, 21, 0.15);
}

.capacity-title {
  font-size: 14px;
  color: #8c5e2d;
  text-transform: uppercase;
  letter-spacing: 2px;
}

.capacity-values {
  font-size: 28px;
  margin: 6px 0;
}

.capacity-bar {
  width: 100%;
  height: 12px;
  background: #f1dec4;
  border-radius: 10px;
  overflow: hidden;
}

.capacity-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #d8881f, #e4b658);
}

.capacity-tip {
  font-size: 12px;
  color: #8c6f46;
  margin-top: 4px;
}

.section-header {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: baseline;
  margin-bottom: 12px;
}

.section-header h2 {
  margin: 0;
  font-size: 20px;
}

.section-header .sub {
  font-size: 13px;
  color: #8d7352;
}

.inventory-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 14px;
}

.inventory-card {
  border: 1px solid rgba(74, 43, 11, 0.12);
  border-radius: 12px;
  padding: 14px;
  background: linear-gradient(135deg, #fffefc, #fff3df);
  min-height: 170px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.item-headline {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tag {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 999px;
  border: 1px solid rgba(74, 43, 11, 0.2);
  text-transform: uppercase;
}

.desc {
  font-size: 12px;
  color: #7e6750;
  flex: 1;
}

.meta-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #6b5235;
}

.storage-table {
  border: 1px solid rgba(74, 43, 11, 0.12);
  border-radius: 10px;
  overflow: hidden;
}

.storage-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1.2fr 1fr;
  gap: 12px;
  padding: 10px 16px;
  align-items: center;
  font-size: 14px;
}

.storage-header {
  background: rgba(74, 43, 11, 0.05);
  font-weight: bold;
}

.badge {
  background: #d78100;
  color: #fff;
  padding: 2px 6px;
  border-radius: 999px;
  font-size: 11px;
}

.own-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}

.own-card {
  border: 1px dashed rgba(74, 43, 11, 0.2);
  border-radius: 12px;
  padding: 14px;
  background: rgba(248, 233, 207, 0.4);
}

.own-card p {
  margin: 4px 0;
  font-size: 13px;
}

.empty {
  text-align: center;
  color: #8a6a45;
  padding: 20px 0;
  font-size: 14px;
}

.btn {
  border: none;
  border-radius: 999px;
  padding: 8px 18px;
  font-size: 13px;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn.primary {
  background: linear-gradient(120deg, #d78100, #f0b74a);
  color: #fff;
  box-shadow: 0 4px 12px rgba(216, 129, 0, 0.35);
}

.btn.primary:hover:not(:disabled) {
  transform: translateY(-1px);
}

.btn.ghost {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.8);
  color: #fff;
}

.btn.outline {
  background: transparent;
  border: 1px solid rgba(74, 43, 11, 0.4);
  color: #4a2b0b;
}

.btn.small {
  align-self: flex-start;
  padding: 6px 14px;
}

.btn.tiny {
  padding: 4px 10px;
  font-size: 12px;
}

.dialog-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.dialog {
  background: #fff8ec;
  padding: 24px;
  border-radius: 20px;
  width: min(420px, 90vw);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.25);
}

.dialog h3 {
  margin: 0 0 8px;
}

.dialog-tip {
  font-size: 13px;
  color: #8a6a45;
}

.dialog input {
  width: 100%;
  margin-top: 6px;
  padding: 8px 10px;
  border-radius: 8px;
  border: 1px solid rgba(74, 43, 11, 0.2);
  font-size: 16px;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 18px;
}

.error {
  color: #c0392b;
}
</style>
