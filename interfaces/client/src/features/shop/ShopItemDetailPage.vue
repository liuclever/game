<script setup>
import { useMessage } from '@/composables/useMessage'
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()

const { message, messageType, showMessage } = useMessage()

const item = ref(null)
const quantity = ref(1)
const gold = ref(0)
const yuanbao = ref(0)
const currency = ref('gold')
const loading = ref(true)

// 加载商品详情
const loadItemDetail = async () => {
  const itemId = parseInt(route.params.id)
  try {
    const res = await http.get('/shop/item/' + itemId)
    if (res.data.ok) {
      item.value = res.data.item
      gold.value = res.data.gold
      yuanbao.value = res.data.yuanbao
      currency.value = res.data.currency
    }
  } catch (e) {
    console.error('加载商品详情失败', e)
  } finally {
    loading.value = false
  }
}

// 购买商品
const buyItem = async () => {
  if (!item.value) return
  if (quantity.value < 1) {
    return
  }
  
  try {
    const res = await http.post('/shop/buy', {
      shop_item_id: item.value.id,
      quantity: quantity.value
    })
    if (res.data.ok) {
      // 跳转到购买成功页面
      const category = route.query.category || 'copper'
      router.push({
        path: '/shop/success',
        query: {
          name: item.value.name,
          quantity: quantity.value,
          cost: item.value.price * quantity.value,
          currency: currency.value,
          category: category
        }
      })
    } else {
      // 错误时仍然使用提示
      showMessage(res.data.error, 'error')
    }
  } catch (e) {
    console.error('购买失败', e)
    showMessage('购买失败', 'error')
  }
}

// 返回前页
const goBack = () => {
  const category = route.query.category || 'copper'
  router.push('/shop?category=' + category)
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
    <!-- 消息提示 -->
    <div v-if="message" class="message" :class="messageType">
      {{ message }}
    </div>

    <div v-if="loading">加载中...</div>
    <template v-else-if="item">
      <!-- 商品信息 -->
      <div class="item-name">{{ item.name }}</div>
      <div class="item-desc">{{ item.description }}</div>
      <div class="item-price">价格:{{ item.price }}{{ currency === 'gold' ? '铜钱' : '元宝' }}</div>
      
      <!-- 购买区域 -->
      <div class="buy-section">
        <span>购买数量:</span>
        <input type="number" v-model.number="quantity" min="1" class="qty-input" />
        <button class="buy-btn" @click="buyItem">购买</button>
      </div>

      <!-- 货币显示 -->
      <div class="currency-info">
        <div>铜钱:{{ gold }}</div>
        <div>元宝:{{ yuanbao }}</div>
      </div>
    </template>
    <div v-else>商品不存在</div>

    <!-- 返回链接 -->
    <div class="nav-links">
      <a class="link" @click="goBack">返回前页</a>
      <div><a class="link" @click="goHome">返回游戏首页</a></div>
    </div>

  </div>
</template>

<style scoped>
.detail-page {
  background: #FFF8DC;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 13px;
  line-height: 1.8;
  font-family: SimSun, "宋体", serif;
}

.item-name {
  color: #CC3300;
  font-weight: bold;
}

.item-desc {
  color: #000;
  /* 商城描述来是长文案；允许换行避免被挤压 */
  white-space: pre-wrap;
  word-break: break-word;
}

.item-price {
  color: #000;
}

.buy-section {
  margin: 8px 0;
}

.qty-input {
  width: 50px;
  padding: 2px 4px;
  border: 1px solid #999;
  font-size: 13px;
}

.buy-btn {
  padding: 2px 8px;
  font-size: 12px;
  cursor: pointer;
}

.currency-info {
  margin: 12px 0;
}

.nav-links {
  margin-top: 16px;
  padding-top: 10px;
  border-top: 1px solid #CCCCCC;
}

.link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.footer {
  margin-top: 10px;
}

.gray {
  color: #666666;
}

.small {
  font-size: 11px;
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
