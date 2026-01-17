<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import http from '@/services/http'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const item = ref(null)
const quantity = ref(1)
const maxQuantity = ref(1)

// 加载道具信息
const loadItem = async () => {
  try {
    const invItemId = route.query.id
    if (!invItemId) {
      console.error('缺少道具ID')
      router.push('/inventory')
      return
    }

    // 获取背包列表，找到对应的道具
    const res = await http.get('/inventory/list')
    if (res.data.ok) {
      const found = res.data.items.find(i => i.id == invItemId)
      if (!found) {
        console.error('道具不存在')
        router.push('/inventory')
        return
      }
      item.value = found
      maxQuantity.value = found.quantity
      quantity.value = 1
    } else {
      console.error('加载失败')
      router.push('/inventory')
    }
  } catch (e) {
    console.error('加载道具失败', e)
    router.push('/inventory')
  } finally {
    loading.value = false
  }
}

import { getItemUseRoute } from '@/utils/itemUseRoutes'

// 使用道具
const useItem = async () => {
  if (!item.value) return
  
  const qty = quantity.value
  if (qty < 1 || qty > maxQuantity.value) {
    console.error('数量无效')
    return
  }

  // 检查是否有特殊的使用路由
  const useRoute = getItemUseRoute(item.value.item_id, item.value.name)
  if (useRoute) {
    // 跳转到对应的使用窗口
    router.push(useRoute)
    return
  }

  // 没有特殊路由的道具，使用默认的直接使用逻辑
  try {
    const res = await http.post('/inventory/use', {
      id: item.value.id,
      quantity: qty
    })

    if (res.data.ok) {
      // 跳转到结果页面
      router.push({
        path: '/inventory/item/result',
        query: {
          itemName: item.value.name,
          quantity: qty,
          message: res.data.message || '使用成功',
          rewards: JSON.stringify(res.data.rewards || {})
        }
      })
    } else {
      console.error(`使用失败: ${res.data.error || '未知错误'}`)
    }
  } catch (e) {
    console.error('使用道具失败', e)
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
  loadItem()
})
</script>

<template>
  <div class="use-select-page">
    <div v-if="loading" class="section gray">加载中...</div>
    
    <template v-else-if="item">
      <div class="section title">【{{ item.action_name || '使用' }}道具】</div>
      
      <div class="section">
        <div class="item-name">{{ item.name }}</div>
        <div class="item-info">拥有数量：{{ item.quantity }}</div>
        <div class="item-desc" v-if="item.description">{{ item.description }}</div>
      </div>

      <div class="section">
        <div>选择{{ item.action_name || '使用' }}数量：</div>
        <input 
          type="number" 
          v-model.number="quantity" 
          :min="1" 
          :max="maxQuantity"
          class="quantity-input"
        />
        <div class="hint">（最多{{ maxQuantity }}个）</div>
      </div>

      <div class="section">
        <a class="link btn-link" @click="useItem">{{ item.action_name || '使用' }}</a>
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
.use-select-page {
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
  font-size: 18px;
  margin-bottom: 8px;
}

.item-info {
  color: #666;
  margin-bottom: 8px;
}

.item-desc {
  color: #000;
  margin-top: 8px;
  padding: 8px;
  background: #f5f5f5;
  border-radius: 4px;
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

.gray {
  color: #666666;
}
</style>
