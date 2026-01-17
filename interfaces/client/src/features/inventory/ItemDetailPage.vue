<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import http from '@/services/http'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const item = ref(null)
const recycleQuantity = ref(1)

// 加载道具详情
const loadItemDetail = async () => {
  try {
    const invItemId = route.query.id
    if (!invItemId) {
      console.error('缺少道具ID')
      router.push('/inventory')
      return
    }

    const res = await http.get(`/inventory/item/detail?id=${invItemId}`)
    if (res.data.ok) {
      item.value = res.data.item
      recycleQuantity.value = 1
    } else {
      console.error(res.data.error || '加载失败')
      router.push('/inventory')
    }
  } catch (e) {
    console.error('加载道具详情失败', e)
    router.push('/inventory')
  } finally {
    loading.value = false
  }
}

// 回收道具
const recycleItem = async () => {
  if (!item.value) return

  const qty = recycleQuantity.value
  if (qty < 1 || qty > item.value.quantity) {
    console.error('数量无效')
    return
  }

  if (!confirm(`确定要回收 ${item.value.name}×${qty} 吗？`)) {
    return
  }

  try {
    const res = await http.post('/inventory/recycle', {
      id: item.value.id,
      quantity: qty
    })

    if (res.data.ok) {
      console.log(res.data.message || '回收成功')
      // 刷新道具信息
      await loadItemDetail()
    } else {
      console.error(`回收失败: ${res.data.error || '未知错误'}`)
    }
  } catch (e) {
    console.error('回收道具失败', e)
  }
}

import { getItemUseRoute } from '@/utils/itemUseRoutes'

// 跳转到使用选择页或特殊使用窗口
const goToUse = () => {
  if (!item.value || !item.value.can_use_or_open) {
    console.log('该道具无法使用')
    return
  }
  
  // 检查是否有特殊的使用路由
  const useRoute = getItemUseRoute(item.value.item_id, item.value.name)
  if (useRoute) {
    // 直接跳转到对应的使用窗口
    router.push(useRoute)
  } else {
    // 没有特殊路由的道具，跳转到使用选择页
    router.push({ path: '/inventory/item/use', query: { id: item.value.id } })
  }
}

// 返回背包
const goBack = () => {
  router.push('/inventory')
}

// 返回首页
const goHome = () => {
  router.push('/')
}

onMounted(() => {
  loadItemDetail()
})
</script>

<template>
  <div class="detail-page">
    <div v-if="loading" class="section gray">加载中...</div>
    
    <template v-else-if="item">
      <div class="section title">【道具详情】</div>
      
      <div class="section">
        <div class="item-name">{{ item.name }}</div>
        <div class="item-info">拥有数量：{{ item.quantity }}</div>
        <div class="item-type">类型：{{ item.type === 'consumable' ? '道具' : item.type === 'material' ? '材料' : item.type }}</div>
      </div>

      <div class="section" v-if="item.description">
        <div class="desc-title">描述：</div>
        <div class="item-desc">{{ item.description }}</div>
      </div>

      <div class="section" v-if="item.can_use_or_open">
        <a class="link btn-link" @click="goToUse">{{ item.action_name || '使用' }}</a>
      </div>

      <div class="section divider">
        <div class="divider-line"></div>
        <div class="divider-text">回收</div>
        <div class="divider-line"></div>
      </div>

      <div class="section">
        <div>回收数量：</div>
        <input 
          type="number" 
          v-model.number="recycleQuantity" 
          :min="1" 
          :max="item.quantity"
          class="quantity-input"
        />
        <div class="hint">（最多{{ item.quantity }}个）</div>
        <div class="hint">回收将获得少量铜钱</div>
      </div>

      <div class="section">
        <a class="link btn-link danger" @click="recycleItem">回收</a>
      </div>

      <div class="section">
        <a class="link" @click="goBack">返回背包</a>
      </div>
      <div class="section">
        <a class="link" @click="goHome">返回游戏首页</a>
      </div>
    </template>
  </div>
</template>

<style scoped>
.detail-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 17px;
  line-height: 1.8;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 8px 0;
}

.title {
  font-weight: bold;
  font-size: 18px;
  margin-bottom: 12px;
}

.item-name {
  color: #CC3300;
  font-weight: bold;
  font-size: 20px;
  margin-bottom: 8px;
}

.item-info {
  color: #666;
  margin-bottom: 4px;
}

.item-type {
  color: #666;
  margin-bottom: 8px;
}

.desc-title {
  font-weight: bold;
  margin-bottom: 4px;
}

.item-desc {
  color: #000;
  padding: 8px;
  background: #f5f5f5;
  border-radius: 4px;
  white-space: pre-wrap;
  word-break: break-word;
}

.quantity-input {
  width: 80px;
  padding: 4px 8px;
  font-size: 16px;
  border: 1px solid #CCCCCC;
  margin: 8px 0;
}

.hint {
  color: #666;
  font-size: 14px;
  margin-top: 4px;
}

.link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: none;
  margin-right: 12px;
}

.link:hover {
  text-decoration: underline;
}

.btn-link {
  display: inline-block;
  padding: 6px 16px;
  background: #f0f0f0;
  border: 1px solid #CCCCCC;
  border-radius: 4px;
  margin-right: 8px;
  margin-top: 8px;
}

.btn-link:hover {
  background: #e0e0e0;
}

.btn-link.danger {
  background: #f8d7da;
  color: #721c24;
  border-color: #f5c6cb;
}

.btn-link.danger:hover {
  background: #f5c6cb;
}

.divider {
  display: flex;
  align-items: center;
  margin: 16px 0;
}

.divider-line {
  flex: 1;
  height: 1px;
  background: #CCCCCC;
}

.divider-text {
  padding: 0 12px;
  color: #666;
  font-size: 14px;
}

.gray {
  color: #666666;
}
</style>
