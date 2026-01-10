<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()

const currentAmount = ref(0)
const redeemAmount = ref(1)
const loading = ref(false)
const errorMessage = ref('')
const isRedeeming = ref(false)

const fetchCurrentAmount = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const res = await http.get('/exchange/item/god-crystal/status')
    if (res.data?.ok) {
      currentAmount.value = res.data.current_fragment ?? 0
    } else {
      throw new Error(res.data?.error || '加载进化碎片数量失败')
    }
  } catch (err) {
    console.error(err)
    errorMessage.value = err.message || '加载进化碎片数量失败'
    alert(errorMessage.value)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchCurrentAmount()
})

const handleRedeem = async () => {
  if (isRedeeming.value) return
  if (redeemAmount.value < 1) {
    alert('兑换数量需大于 0')
    return
  }

  isRedeeming.value = true
  try {
    const res = await http.post('/exchange/item/god-crystal', { count: redeemAmount.value })
    if (res.data?.ok) {
      alert(res.data.message || `兑换成功，获得进化圣水晶×${redeemAmount.value}`)
      await fetchCurrentAmount()
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

const goBack = () => router.back()
const goHome = () => router.push('/')
</script>

<template>
  <div class="exchange-god-crystal-page">
    <div class="section title">【兑换】进化圣水晶</div>
    <div class="section">幻兽进化到天界所需材料</div>
    <div class="section">[指引]: 集齐30进化碎片</div>
    <div class="section">
      [当前数量]: {{ loading ? '加载中…' : currentAmount }}枚进化碎片
    </div>
    <div v-if="errorMessage" class="section gray">提示：{{ errorMessage }}</div>
    <div class="section">[奖励]: 进化圣水晶</div>
    <div class="section form">
      <label>
        兑换数量：
        <input type="number" min="1" v-model.number="redeemAmount" />
      </label>
      <button :disabled="isRedeeming" @click="handleRedeem">
        {{ isRedeeming ? '兑换中…' : '确定' }}
      </button>
    </div>

    <div class="section"><a class="link" @click="goBack">返回前页</a></div>
    <div class="section"><a class="link" @click="goHome">返回游戏首页</a></div>
  </div>
</template>

<style scoped>
.exchange-god-crystal-page {
  padding: 16px;
  line-height: 1.8;
  color: #111;
}

.section {
  margin-bottom: 8px;
}

.title {
  font-weight: bold;
  margin-bottom: 12px;
}

.form {
  display: flex;
  align-items: center;
  gap: 8px;
}

input[type='number'] {
  width: 60px;
}

.link,
.exchange-god-crystal-page a {
  color: #1e4fd8;
  text-decoration: none;
}

.link:hover,
.exchange-god-crystal-page a:hover {
  text-decoration: underline;
}

.gray {
  color: #666;
}
</style>
