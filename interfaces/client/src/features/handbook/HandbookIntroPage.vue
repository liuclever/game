<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

// 仅展示文案的“图鉴简介”页：用于模仿原站交互，不依赖任何外站 URL/数据。
const goBack = () => router.back()
const goHome = () => router.push('/')
</script>

<template>
  <div class="handbook-intro">
    <div class="section title">【图鉴】简介</div>

    <div class="section">亲爱的召唤师:</div>
    <div class="section">皇家召唤协会发布图鉴系统.</div>
    <div class="section">[幻兽图鉴]是召唤师旅行必备工具,记录召唤师遇到并成功召唤的所有幻兽.</div>
    <div class="section">幻兽被召唤后,即可自动点亮对应图鉴,还能看到幻兽终极属性.</div>

    <div class="section spacer">
      <a class="link" @click="goBack">返回前页</a>
    </div>
    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>
  </div>
</template>

<style scoped>
.handbook-intro {
  background: #FFF8DC;
  min-height: 100vh;
  padding: 14px 14px;
  font-size: 18px;
  line-height: 1.8;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 10px 0;
}

.title {
  font-weight: bold;
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


