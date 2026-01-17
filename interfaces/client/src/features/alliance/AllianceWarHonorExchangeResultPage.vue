<script setup>
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// 从URL参数获取兑换结果
const success = route.query.success === 'true'
const message = route.query.message || ''
const itemName = route.query.itemName || ''
const quantity = route.query.quantity || 0
const honorCost = route.query.honorCost || 0
const remainingHonor = route.query.remainingHonor || 0

const goBack = () => {
  router.push('/alliance/war/honor')
}

const goWar = () => {
  router.push('/alliance/war')
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
    <div class="section title">【战功兑换结果】</div>

    <div v-if="success" class="section">
      <div class="success-msg">{{ message || '兑换成功' }}</div>
      <div v-if="itemName" class="section">
        获得：{{ quantity }}{{ itemName }}
      </div>
      <div v-if="honorCost" class="section">
        消耗战功：{{ honorCost }}
      </div>
      <div v-if="remainingHonor !== undefined" class="section">
        剩余战功：{{ remainingHonor }}
      </div>
    </div>

    <div v-else class="section">
      <div class="error-msg">{{ message || '兑换失败' }}</div>
    </div>

    <div class="section spacer">
      <a class="link" @click.prevent="goBack">返回战功兑换</a>
    </div>
    <div class="section">
      <a class="link" @click.prevent="goWar">返回盟战</a>
    </div>
    <div class="section">
      <a class="link" @click.prevent="goAlliance">返回联盟</a>
    </div>
    <div class="section">
      <a class="link" @click.prevent="goHome">返回游戏首页</a>
    </div>
  </div>
</template>

<style scoped>
.result-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 10px 14px 24px;
  font-size: 16px;
  line-height: 1.7;
  font-family: SimSun, '宋体', serif;
}

.section {
  margin: 6px 0;
}

.title {
  font-weight: bold;
  font-size: 18px;
}

.spacer {
  margin-top: 16px;
}

.success-msg {
  color: #0a840a;
}

.error-msg {
  color: #c03;
}

.link {
  color: #0066cc;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}
</style>
