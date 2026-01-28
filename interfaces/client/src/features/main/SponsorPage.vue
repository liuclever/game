<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'
import MainMenuLinks from '@/features/main/components/MainMenuLinks.vue'

const router = useRouter()
const route = useRoute()

const loading = ref(true)
const errorMessage = ref('')
const exchangeAmount = ref('')
const exchanging = ref(false)
const paying = ref(false)
const selectedProduct = ref(null)
const showConfirm = ref(false)

const sponsorInfo = ref({
  silverDiamond: 0,
  yuanbao: 0,
  vipLevel: 0,
  vipExp: 0,
  firstRechargeAvailable: true,
})

const products = ref([])
const exchangeRate = ref(100)

const convertedYuanbao = computed(() => {
  const amount = Number(exchangeAmount.value)
  if (!amount || amount <= 0) return 0
  return amount * exchangeRate.value
})

const loadSponsorInfo = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const res = await http.get('/pay/products')
    if (res.data?.ok) {
      products.value = res.data.products || []
      exchangeRate.value = res.data.exchange_rate || 100
      sponsorInfo.value = {
        silverDiamond: res.data.silver_diamond || 0,
        yuanbao: res.data.yuanbao || 0,
        vipLevel: res.data.vip_level || 0,
        vipExp: res.data.vip_exp || 0,
        firstRechargeAvailable: res.data.first_recharge_available,
      }
    } else {
      errorMessage.value = res.data?.error || '加载失败'
    }
  } catch (err) {
    console.error('加载赞助信息失败', err)
    errorMessage.value = '加载失败，请稍后再试'
  } finally {
    loading.value = false
  }
}

const handleBuy = (product) => {
  selectedProduct.value = product
  showConfirm.value = true
}

const cancelOrder = () => {
  showConfirm.value = false
  selectedProduct.value = null
}

const submitOrder = async () => {
  if (paying.value || !selectedProduct.value) return
  paying.value = true
  try {
    const res = await http.post('/pay/create-order', {
      product_id: selectedProduct.value.id,
      pay_type: 'page',
    })
    if (res.data?.ok && res.data.pay_url) {
      window.location.href = res.data.pay_url
    } else {
      alert(res.data?.error || '创建订单失败')
    }
  } catch (err) {
    console.error('创建订单失败', err)
    alert('创建订单失败，请稍后再试')
  } finally {
    paying.value = false
  }
}

const handleExchange = async () => {
  if (exchanging.value) return
  const amount = Number(exchangeAmount.value)
  if (!amount || amount <= 0) {
    alert('请输入有效的宝石数量')
    return
  }
  if (amount > sponsorInfo.value.silverDiamond) {
    alert('宝石不足')
    return
  }
  exchanging.value = true
  try {
    const res = await http.post('/pay/exchange', { amount })
    if (res.data?.ok) {
      alert(res.data.message)
      sponsorInfo.value.silverDiamond = res.data.silver_diamond
      sponsorInfo.value.yuanbao = res.data.yuanbao
      exchangeAmount.value = ''
    } else {
      alert(res.data?.error || '兑换失败')
    }
  } catch (err) {
    console.error('兑换失败', err)
    alert('兑换失败，请稍后再试')
  } finally {
    exchanging.value = false
  }
}

const goBack = () => {
  router.push('/')
}

const goPrev = () => {
  router.back()
}

const goHome = () => {
  router.push('/')
}

const goVip = () => {
  router.push('/vip')
}

const goMonthCard = () => {
  router.push('/sponsor/month-card')
}

onMounted(() => {
  if (route.query.result === 'success') {
    alert('支付完成，宝石将在几秒内到账')
  }
  loadSponsorInfo()
})
</script>

<template>
  <div class="sponsor-page">
    <div class="section">【赞助中心】</div>
    
    <div v-if="loading" class="section">加载中...</div>
    <div v-else-if="errorMessage" class="section error">{{ errorMessage }}</div>
    <template v-else>
      <div class="section">
        当前宝石: <span class="diamond">{{ sponsorInfo.silverDiamond }}</span>
        | 当前元宝: <span class="yuanbao">{{ sponsorInfo.yuanbao }}</span>
      </div>
      
      <div class="section">
        VIP等级: <span class="vip">VIP{{ sponsorInfo.vipLevel }}</span>
        <a class="link" @click="goVip">查看特权</a>
        | <a class="link" @click="goMonthCard">月卡</a>
      </div>
      
      <div class="section">【充值宝石】</div>
      
      <div class="section product-list">
        <span 
          v-for="product in products" 
          :key="product.id"
          class="product-item"
        >
          <a 
            class="link" 
            @click="handleBuy(product)"
            :class="{ disabled: paying }"
          >
            {{ product.name }}(¥{{ product.price }})
          </a>
          <span v-if="product.first_bonus && sponsorInfo.firstRechargeAvailable" class="bonus-tag">首充双倍</span>
        </span>
      </div>
      
      <div class="section hint" v-if="sponsorInfo.firstRechargeAvailable">
        提示：首充双倍仅限一次，建议选择高档位（如1000宝石）以获得最大收益！
      </div>
      <div class="section hint" v-else>
        首充双倍已使用
      </div>
      
      <div class="section" v-if="paying">
        正在跳转支付...
      </div>
      
      <!-- 订单确认弹窗 -->
      <div v-if="showConfirm" class="confirm-overlay">
        <div class="confirm-box">
          <div class="confirm-title">确认订单</div>
          <div class="confirm-content">
            <div class="order-row">
              <span class="label">商品名称:</span>
              <span>{{ selectedProduct?.name }}</span>
            </div>
            <div class="order-row">
              <span class="label">商品描述:</span>
              <span>{{ selectedProduct?.description }}</span>
            </div>
            <div class="order-row" v-if="selectedProduct?.first_bonus && sponsorInfo.firstRechargeAvailable">
              <span class="label">首充奖励:</span>
              <span class="bonus">+{{ selectedProduct?.first_bonus }}宝石</span>
            </div>
            <div class="order-total">
              <span>实付款:</span>
              <span class="price">¥{{ selectedProduct?.price }}</span>
            </div>
          </div>
          <div class="confirm-actions">
            <button class="btn-cancel" @click="cancelOrder">取消</button>
            <button class="btn-submit" @click="submitOrder" :disabled="paying">
              {{ paying ? '提交中...' : '提交订单' }}
            </button>
          </div>
        </div>
      </div>
      
      <div class="section">【宝石兑换元宝】</div>
      <div class="section">
        兑换比例: 1宝石 = {{ exchangeRate }}元宝
      </div>
      <div class="section exchange-row">
        输入宝石数量: 
        <input 
          type="number" 
          v-model="exchangeAmount" 
          placeholder="数量"
          class="exchange-input"
          min="1"
        />
        <button 
          class="exchange-btn" 
          @click="handleExchange"
          :disabled="exchanging"
        >
          {{ exchanging ? '兑换中...' : '兑换' }}
        </button>
        <span v-if="convertedYuanbao"> = {{ convertedYuanbao }}元宝</span>
      </div>
      
      <div class="section">【说明】</div>
      <div class="section notice">
        《梦炽云召唤之星》感谢您的支持！充值的宝石可兑换元宝，用于购买游戏道具。充值即表示您同意本游戏的用户协议。
      </div>
    </template>
    
    <!-- 分隔线 -->
    <div class="divider"></div>

    <!-- 底部菜单（严格按“新人战力榜排行”页实现方式复刻） -->
    <MainMenuLinks />

    <!-- 导航 -->
    <div class="section nav-links">
      <a class="link" @click="goPrev">返回前页</a>
    </div>
    <div class="section nav-links">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>
  </div>
</template>

<style scoped>
.sponsor-page {
  min-height: 100vh;
  background: #FFFFFF;
  padding: 10px 15px;
  font-size: 17px;
  color: #333;
  font-family: 'SimSun', '宋体', serif;
  line-height: 1.8;
}

.divider {
  border-top: 1px dashed #CCCCCC;
  margin: 12px 0;
}

.nav-links {
  margin: 2px 0;
}

.section {
  margin: 4px 0;
}

.link {
  color: #0066cc;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.link.disabled {
  color: #999;
  pointer-events: none;
}

.diamond {
  color: #9c27b0;
  font-weight: bold;
}

.yuanbao {
  color: #ff9800;
  font-weight: bold;
}

.vip {
  color: #e91e63;
  font-weight: bold;
}

.highlight {
  color: #f44336;
  font-weight: bold;
}

.product-list {
  line-height: 2.2;
}

.product-item {
  margin-right: 15px;
  white-space: nowrap;
}

.bonus-tag {
  color: #f44336;
  font-size: 18px;
  margin-left: 2px;
}

.exchange-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 5px;
}

.exchange-input {
  width: 80px;
  padding: 2px 5px;
  border: 1px solid #999;
  font-size: 17px;
}

.exchange-btn {
  padding: 2px 10px;
  background: #FFFFFF;
  border: 1px solid #999;
  cursor: pointer;
  font-size: 17px;
}

.exchange-btn:hover {
  background: #e8e8c8;
}

.exchange-btn:disabled {
  color: #999;
  cursor: not-allowed;
}

.notice {
  color: #666;
  font-size: 18px;
}

.hint {
  color: #f60;
  font-size: 18px;
}

.error {
  color: #c62828;
}

/* 订单确认弹窗 */
.confirm-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.confirm-box {
  background: #fff;
  border-radius: 8px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}

.confirm-title {
  background: #ffffff;
  padding: 12px 15px;
  font-size: 16px;
  font-weight: bold;
  border-bottom: 1px solid #ddd;
  border-radius: 8px 8px 0 0;
}

.confirm-content {
  padding: 15px;
}

.order-row {
  display: flex;
  margin: 8px 0;
  font-size: 17px;
}

.order-row .label {
  color: #666;
  width: 80px;
  flex-shrink: 0;
}

.order-row .bonus {
  color: #f44336;
  font-weight: bold;
}

.order-total {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px dashed #ddd;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 10px;
}

.order-total .price {
  color: #e53935;
  font-size: 24px;
  font-weight: bold;
}

.confirm-actions {
  display: flex;
  border-top: 1px solid #ddd;
}

.confirm-actions button {
  flex: 1;
  padding: 12px;
  font-size: 16px;
  border: none;
  cursor: pointer;
}

.btn-cancel {
  background: #ffffff;
  color: #666;
  border-radius: 0 0 0 8px;
}

.btn-submit {
  background: #e53935;
  color: #fff;
  border-radius: 0 0 8px 0;
}

.btn-submit:disabled {
  background: #ffffff;
  cursor: not-allowed;
}
</style>
