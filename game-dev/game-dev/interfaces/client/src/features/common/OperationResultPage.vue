<script setup>
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// 从URL参数获取结果信息
const success = route.query.success === 'true' || route.query.success === true
const title = route.query.title || (success ? '操作成功' : '操作失败')
const message = route.query.message || (success ? '操作已成功完成' : '操作失败')
const detail = route.query.detail || ''
const backPath = route.query.backPath || '/'
const backText = route.query.backText || '返回'
const showHome = route.query.showHome !== 'false'

const goBack = () => {
  router.push(backPath)
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="result-page">
    <!-- 标题 -->
    <div :class="['title', success ? 'success' : 'error']">{{ title }}</div>
    
    <!-- 主要消息 -->
    <div class="message">{{ message }}</div>
    
    <!-- 详细信息 -->
    <div v-if="detail" class="detail">{{ detail }}</div>

    <!-- 导航链接 -->
    <div class="nav-links">
      <div><a class="link" @click="goBack">{{ backText }}</a></div>
      <div v-if="showHome"><a class="link" @click="goHome">返回游戏首页</a></div>
    </div>
  </div>
</template>

<style scoped>
.result-page {
  background: #FFF8DC;
  min-height: 100vh;
  padding: 20px 12px;
  font-size: 14px;
  line-height: 1.8;
  font-family: SimSun, "宋体", serif;
}

.title {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 16px;
  text-align: center;
}

.title.success {
  color: #52c41a;
}

.title.error {
  color: #ff4d4f;
}

.message {
  color: #000;
  font-size: 16px;
  margin-bottom: 12px;
  text-align: center;
  padding: 12px;
  background: #fff;
  border-radius: 4px;
  border-left: 4px solid #1890ff;
}

.detail {
  color: #666;
  margin-bottom: 16px;
  padding: 12px;
  background: #f5f5f5;
  border-radius: 4px;
  border-left: 4px solid #999;
}

.nav-links {
  margin-top: 24px;
  text-align: center;
}

.nav-links div {
  margin: 8px 0;
}

.link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: none;
  font-size: 14px;
  padding: 8px 16px;
  display: inline-block;
}

.link:hover {
  text-decoration: underline;
}
</style>
