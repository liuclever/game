<script setup>
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// 从URL参数获取签到结果
const success = route.query.success === 'true'
const message = route.query.message || ''

const goBack = () => {
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
    <div class="section title">【盟战签到结果】</div>

    <div v-if="success" class="section">
      {{ message || '签到成功，获得30000铜钱' }}
    </div>

    <div v-else class="section">
      {{ message || '签到失败' }}
    </div>

    <div class="section spacer">
      <a class="link" @click.prevent="goBack">返回盟战</a>
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

.link {
  color: #0066cc;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}
</style>
