<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

// 返回地图首页
const goMap = () => {
  router.push('/map')
}

// 返回游戏首页
const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="success-page">
    <!-- 传送成功 -->
    <div class="section title">传送成功</div>
    
    <!-- 导航 -->
    <div class="section spacer">
      <a class="link" @click="goMap">返回地图首页</a>
    </div>
    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>
    
  </div>
</template>

<style scoped>
.success-page {
  background: #E8F4FC;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 13px;
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

.gray {
  color: #666666;
}

.small {
  font-size: 11px;
}

.footer {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #CCCCCC;
}
</style>
