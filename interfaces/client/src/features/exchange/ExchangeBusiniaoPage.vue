<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()

const REQUIRED_AMOUNT = 4

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
    const res = await http.get('/exchange/beast/businiao/status')
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

const goBack = () => router.back()
const goHome = () => router.push('/')

const handleRedeem = async () => {
  if (isRedeeming.value) return
  if (!exchangeInfo.value.canExchange) {
    alert(`神·逆鳞不足，需要${exchangeInfo.value.required}块`)
    return
  }

  isRedeeming.value = true
  try {
    const res = await http.post('/exchange/beast/businiao')
    if (res.data?.ok) {
      alert(res.data.message || '兑换成功')
      await fetchExchangeInfo()
    } else {
      alert(res.data?.error || '兑换失败')
    }
  } catch (err) {
    console.error(err)
    alert('兑换失败，请稍后重试')
  } finally {
    isRedeeming.value = false
  }
}
</script>

<template>
  <div class="exchange-detail-page">
    <div class="section title">【兑换】神兽[神·不死鸟]</div>

    <div class="section">建议0-49级召唤师兑换：</div>
    <div class="section indent">
      集齐4块[神·逆鳞]，可获得中级神兽[神·不死鸟]，40级可携带！
    </div>
    <div class="section indent">
      神·不死鸟是中级幻兽的王者，且4个技能均为高级技能！
    </div>
    <div class="section indent">
      提示：“远古钛金宝箱”、“远古秘银宝箱”开启有几率获得[神·逆鳞]
    </div>

    <div class="section">[指引]: 集齐4块[神·逆鳞]</div>
    <div class="section">
      [当前数量]: {{ exchangeInfo.currentNilin }}块神·逆鳞
      <span v-if="loading" class="gray">（加载中…）</span>
    </div>
    <div class="section">[奖励]: 神兽[神·不死鸟]</div>
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

    <div class="section"><a class="link" @click="goBack">返回前页</a></div>
    <div class="section"><a class="link" @click="goHome">返回游戏首页</a></div>
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
</style>
