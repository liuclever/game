<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import http from '@/services/http'
import { useMessage } from '@/composables/useMessage'
import MainMenuLinks from '@/features/main/components/MainMenuLinks.vue'

const route = useRoute()
const router = useRouter()
const { message, messageType, showMessage } = useMessage()

const loading = ref(true)
const item = ref(null)
const quantity = ref(1)
const maxQuantity = ref(1)
const allowBatch = ref(false)

const isNilinFragment = computed(() => Number(item.value?.item_id) === 3011)

// 加载道具信息
const loadItem = async () => {
  try {
    const invItemId = route.query.id
    if (!invItemId) {
      showMessage('缺少道具ID', 'error')
      router.push('/inventory')
      return
    }

    // 获取背包列表，找到对应的道具
    const res = await http.get('/inventory/list')
    if (res.data.ok) {
      const found = res.data.items.find(i => i.id == invItemId)
      if (!found) {
        showMessage('道具不存在', 'error')
        router.push('/inventory')
        return
      }
      item.value = found
      // 可批量道具一次最多10个；不可批量的不要实现批量（固定只能选1个）
      // 神·逆鳞碎片(3011)改为“合成机制”：不走批量使用数量选择
      if (Number(found.item_id) === 3011) {
        allowBatch.value = false
        maxQuantity.value = 1
      } else {
        const BATCH_ITEM_IDS = new Set([6003, 6014, 6030, 6007, 6008, 6009, 6010, 6004, 4001, 6013, 7101, 7102, 7103, 7104, 7105, 7106])
        allowBatch.value = BATCH_ITEM_IDS.has(Number(found.item_id))
        maxQuantity.value = allowBatch.value ? Math.min(10, found.quantity) : 1
      }
      quantity.value = 1
    } else {
      showMessage('加载失败', 'error')
      router.push('/inventory')
    }
  } catch (e) {
    console.error('加载道具失败', e)
    showMessage('加载失败', 'error')
    router.push('/inventory')
  } finally {
    loading.value = false
  }
}

import { getItemUseRoute, getItemUseHint } from '@/utils/itemUseRoutes'

// 使用道具
const useItem = async () => {
  if (!item.value) return
  
  const qty = isNilinFragment.value ? 1 : quantity.value
  if (qty < 1 || qty > maxQuantity.value) {
    showMessage('数量无效', 'error')
    return
  }

  // 检查是否有特殊的使用路由
  const useRoute = getItemUseRoute(item.value.item_id, item.value.name)
  if (useRoute) {
    // 按需求：去除提示/弹框，直接跳转到对应功能页
    getItemUseHint(item.value.item_id, item.value.name) // 保留调用以维持兼容（不展示）
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
      showMessage(`使用失败: ${res.data.error || '未知错误'}`, 'error')
    }
  } catch (e) {
    console.error('使用道具失败', e)
    showMessage('请求失败，请稍后再试', 'error')
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
    <!-- 消息提示 -->
    <div v-if="message" class="message" :class="messageType">
      {{ message }}
    </div>

    <div v-if="loading" class="section gray">加载中...</div>
    
    <template v-else-if="item">
      <div class="section title">【{{ isNilinFragment ? '合成' : (item.action_name || '使用') }}道具】</div>
      
      <div class="section">
        <div class="item-name">{{ item.name }}</div>
        <div class="item-info">拥有数量：{{ item.quantity }}</div>
        <div class="item-desc" v-if="item.description">{{ item.description }}</div>
        <template v-if="isNilinFragment">
          <div class="hint">合成规则：每次消耗100块碎片 → 获得1块神·逆鳞</div>
        </template>
      </div>

      <div class="section" v-if="allowBatch">
        <div>选择{{ item.action_name || '使用' }}数量：</div>
        <input
          type="number"
          v-model.number="quantity"
          :min="1"
          :max="maxQuantity"
          class="quantity-input"
        />
        <div class="hint">（一次最多10个，当前最多{{ maxQuantity }}个）</div>
      </div>

      <div class="section">
        <a class="link btn-link" @click="useItem">{{ isNilinFragment ? '合成' : (item.action_name || '使用') }}</a>
      </div>

      <div class="section">
        <a class="link" @click="goBack">返回背包</a>
      </div>
      <!-- 主页菜单（严格复刻主页内容与UI） -->
      <MainMenuLinks />
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
  font-size: 19px;
  line-height: 1.8;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 8px 0;
}

.title {
  font-weight: bold;
  font-size: 20px;
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
  font-size: 18px;
  border: 1px solid #CCCCCC;
  margin: 8px 0;
}

.hint {
  color: #666;
  font-size: 15px;
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
