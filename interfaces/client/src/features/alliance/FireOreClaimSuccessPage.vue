<script setup>
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const itemName = route.query.itemName || '火能原石'
const error = route.query.error

const goAlliance = () => {
  // 直接跳转到联盟页面，添加时间戳确保刷新
  router.push({
    path: '/alliance',
    query: { refresh: '1', _t: Date.now() }
  })
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="success-page">
    <div v-if="error" class="section title error-title">领取失败</div>
    <div v-else class="section title">领取成功</div>
    
    <div v-if="error" class="section message error-message">
      {{ error }}
    </div>
    <template v-else>
      <div class="section message">
        获得{{ itemName }}×1
      </div>
    </template>

    <div class="section spacer">
      <a class="link" @click="goAlliance">返回联盟</a>
    </div>
    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
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

.section {
  margin: 2px 0;
}

.title {
  font-weight: bold;
  margin-bottom: 6px;
}

.error-title {
  color: #CC0000;
}

.message {
  color: #000;
  margin-bottom: 8px;
}

.error-message {
  color: #CC0000;
  font-weight: bold;
}

.cost {
  color: #666;
  margin-bottom: 16px;
}

.spacer {
  margin-top: 16px;
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
