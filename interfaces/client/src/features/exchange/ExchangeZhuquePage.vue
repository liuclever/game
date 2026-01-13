<script setup>
import { useMessage } from '@/composables/useMessage'
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()

const REQUIRED_AMOUNT = 10

const { message, messageType, showMessage } = useMessage()

const exchangeInfo = ref({
  required: REQUIRED_AMOUNT,
  currentNilin: 0,
  hasBall: false,
  canExchange: false,
})

const loading = ref(false)
const isRedeeming = ref(false)

const fetchExchangeInfo = async () => {
  loading.value = true
  try {
    const res = await http.get('/exchange/beast/zhuque/status')
    if (res.data?.ok) {
      exchangeInfo.value = {
        required: res.data.required ?? REQUIRED_AMOUNT,
        currentNilin: res.data.current_nilin ?? 0,
        hasBall: !!res.data.has_ball,
        canExchange: !!res.data.can_exchange,
      }
    }
  } catch (err) {
    console.error('加载兑换状态失败', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchExchangeInfo()
})

const goBack = () => {
  router.back()
}

const goHome = () => {
  router.push('/')
}

const handleRedeem = async () => {
  if (isRedeeming.value) return
  if (!exchangeInfo.value.canExchange) {
    showMessage(`神·逆鳞不足，需要${exchangeInfo.value.required}块`, 'error')
    return
  }

  isRedeeming.value = true
  try {
    const res = await http.post('/exchange/beast/zhuque')
    if (res.data?.ok) {
      showMessage(res.data.message || '兑换成功', 'success')
      await fetchExchangeInfo()
    } else {
      showMessage(res.data?.error || '兑换失败', 'error')
    }
  } catch (err) {
    console.error(err)
    showMessage('兑换失败，请稍后重试', 'error')
  } finally {
    isRedeeming.value = false
  }
}
</script>

<template>
  <div class="exchange-detail-page">
    <!-- 消息提示 -->
    <div v-if="message" class="message" :class="messageType">
      {{ message }}
    </div>

    <div class="section title">【兑换】神兽[神·朱雀]</div>

    <div class="section">
      建议全体召唤师兑换：
    </div>
    <div class="section indent">
      集齐10块[神·逆鳞]，可获得顶级神兽[神·朱雀]，60级可携带！
    </div>
    <div class="section indent">
      神·朱雀是召唤大陆最顶级的幻兽，且4个技能均为高级技能！
    </div>
    <div class="section indent">
      提示：“远古钛金宝箱”、“远古秘银宝箱”开启有几率获得[神·逆鳞]
    </div>

    <div class="section">
      [指引]: 集齐10块[神·逆鳞]
    </div>
    <div class="section">
      [当前数量]: {{ exchangeInfo.currentNilin }}块神·逆鳞
      <span v-if="loading" class="gray">（加载中…）</span>
    </div>
    <div class="section">
      [奖励]: 神兽[神·朱雀]
    </div>
    <div class="section">
      [状态]:
      <a
        class="link"
        :class="{ disabled: !exchangeInfo.canExchange || isRedeeming }"
        @click.prevent="handleRedeem"
      >{{ isRedeeming ? '兑换中…' : '兑换' }}</a>
      <span v-if="!exchangeInfo.canExchange" class="gray">
        （需要{{ exchangeInfo.required }}块神·逆鳞）
      </span>
    </div>

    <div class="section">
      <a class="link" @click="goBack">返回前页</a>
    </div>
    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>
  </div>
</template>

<style scoped>
.exchange-detail-page {
  padding: 16px;
  line-height: 1.8;
}

.link,
.exchange-detail-page a {
  color: #1e4fd8;
  text-decoration: none;
}

.link:hover,
.exchange-detail-page a:hover {
  text-decoration: underline;
}

.link.disabled {
  color: #999;
  pointer-events: none;
  text-decoration: none;
}

.title {
  font-weight: bold;
  margin-bottom: 12px;
}

.indent {
  padding-left: 1em;
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
