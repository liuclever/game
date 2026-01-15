<script setup>
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// 从URL参数获取结果信息
const isSuccess = route.query.success === 'true'
const message = route.query.message || ''
const landName = route.query.land_name || ''

const goWar = () => {
  router.push('/alliance/war')
}

const goTargets = () => {
  router.push('/alliance/war/targets')
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="result-page">
    <div :class="['message', { error: !isSuccess }]">{{ message }}</div>

    <div class="nav-links">
      <div><a class="link" @click="goTargets">返回土地详情</a></div>
      <div><a class="link" @click="goWar">返回盟战</a></div>
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
  color: #000;
  margin-bottom: 16px;
}

.message.error {
  color: #cc0000;
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
