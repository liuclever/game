<script setup>
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// 从URL参数获取报名信息
const armyLabel = route.query.army_label || ''

const goWar = () => {
  router.push('/alliance/war')
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="success-page">
    <div class="message">报名成功，你被分配至{{ armyLabel }}</div>

    <div class="nav-links">
      <div><a class="link" @click="goWar">返回联盟</a></div>
      <div><a class="link" @click="goHome">返回游戏首页</a></div>
    </div>

  </div>
</template>

<style scoped>
.success-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 17px;
  line-height: 1.8;
  font-family: SimSun, "宋体", serif;
}

.message {
  color: #000;
  margin-bottom: 16px;
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
