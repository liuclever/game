<script setup>
import { useRouter, useRoute } from 'vue-router'
import { computed } from 'vue'

const router = useRouter()
const route = useRoute()

const isSuccess = computed(() => route.query.success === 'true')
const message = computed(() => route.query.message || (isSuccess.value ? '操作成功' : '操作失败'))
const operation = computed(() => route.query.operation || 'unknown') // 'deposit' or 'withdraw'
const itemName = computed(() => route.query.itemName || '')

const goBack = () => {
  router.push({
    path: '/alliance/item-storage',
    query: { refresh: '1', _t: Date.now() }
  })
}

const goAlliance = () => {
  router.push('/alliance')
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="result-page">
    <div :class="['message', { 'success': isSuccess, 'error': !isSuccess }]">
      {{ message }}
    </div>

    <div v-if="isSuccess && itemName" class="detail">
      <span v-if="operation === 'deposit'">已成功寄存 {{ itemName }}</span>
      <span v-else-if="operation === 'withdraw'">已成功取出 {{ itemName }}</span>
    </div>

    <div class="nav-links">
      <div><a class="link" @click="goBack">返回寄存仓库</a></div>
      <div><a class="link" @click="goAlliance">返回联盟</a></div>
      <div><a class="link" @click="goHome">返回游戏首页</a></div>
    </div>
  </div>
</template>

<style scoped>
.result-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 17px;
  line-height: 1.8;
  font-family: SimSun, "宋体", serif;
}

.message {
  margin-bottom: 16px;
  font-weight: bold;
}

.message.success {
  color: green;
}

.message.error {
  color: red;
}

.detail {
  margin-bottom: 16px;
  color: #333;
}

.nav-links {
  margin-top: 16px;
}

.nav-links div {
  margin: 4px 0;
}

.link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}
</style>
