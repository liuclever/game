<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

// 返回竞技场
const goBack = () => {
  router.push('/pvp')
}

// 返回首页
const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="intro-page">
    <!-- 标题 -->
    <div class="section title">【连胜竞技规则】</div>

    <!-- 规则 -->
    <div class="section">系统开放时间：08:00-24:00</div>
    <div class="section">1.每天连胜最多的玩家会成为连胜王，并可以获得连胜王奖励</div>
    <div class="section">2.系统按等级段匹配对手（20-29级、30-39级...），只会匹配同等级段的玩家</div>
    <div class="section">3.每5分钟刷新一次对手，可使用50元宝立即刷新（有概率换到等级更低的对手）</div>
    <div class="section">4.6连胜奖励未达到前，每次切磋消耗100活力；6连胜奖励达成后，每次切磋消耗15活力</div>
    <div class="section">5.达到指定的连胜次数可以获得相对应的奖励（最高6连胜）</div>
    <div class="section">6.切磋胜利连胜+1，切磋失败连胜归零</div>
    <div class="section">7.被别人挑战失败不会影响自己的连胜次数</div>
    <div class="section">8.今日最高连胜次数每天凌晨清零</div>

    <!-- 返回 -->
    <div class="nav-links">
      <div><a class="link" @click="goBack">返回连胜竞技场</a></div>
      <div><a class="link" @click="goHome">返回游戏首页</a></div>
    </div>

  </div>
</template>

<style scoped>
.intro-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 10px 12px;
  font-size: 17px;
  line-height: 1.8;
  font-family: SimSun, "宋体", serif;
}

.title {
  font-weight: bold;
  color: #333;
  margin-bottom: 10px;
}

.section {
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

.gray {
  color: #666;
}

.nav-links {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #ccc;
}

.footer {
  margin-top: 20px;
}

.small {
  font-size: 17px;
}
</style>
