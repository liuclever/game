<script setup>
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// 从URL参数获取结果信息
const success = route.query.success === 'true'
const message = route.query.message || (success ? '签到成功' : '签到失败')
const error = route.query.error || ''

const goCompetition = () => {
  router.push('/alliance/competition')
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
    <div v-if="success" class="message success">
      {{ message }}
    </div>
    <div v-else class="message error">
      {{ error || message }}
    </div>

    <div class="nav-links">
      <div><a class="link" @click="goCompetition">返回争霸赛</a></div>
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
  padding: 8px;
  border-radius: 4px;
}

.message.success {
  color: #006600;
  background-color: #f0f8f0;
  border: 1px solid #00cc00;
}

.message.error {
  color: #cc0000;
  background-color: #fff0f0;
  border: 1px solid #ff0000;
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
