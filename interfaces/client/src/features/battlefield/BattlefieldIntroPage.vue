<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

// 返回战场
const goBack = () => {
  router.push('/battlefield')
}

// 返回首页
const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="intro-page">
    <!-- 标题 -->
    <div class="section title">【战场规则】</div>

    <!-- 规则列表 -->
    <div class="section">1.玩家达到20级可参加古战场，报名古战场消耗20活力。</div>
    <div class="section">2.古战场每天举行一次，06:00-20:00为报名时间，00:00-06:00为战斗时间。</div>
    <div class="section">3.玩家只能参加对应等级的战场，猛虎战场（20-39级）、飞鹤战场（40-100）。</div>
    <div class="section">4.报名的玩家不分阵营，由系统自动匹配对战。</div>
    <div class="section">5.获得人头数最多的玩家为战王，每胜利一场则累积人头一个。轮空不累积人头。</div>
    <div class="section">6.杀敌一定数量可获得杀戮礼包，杀戮礼包会自动放置到背包中。</div>

    <!-- 返回 -->
    <div class="nav-links">
      <div><a class="link" @click="goBack">返回战场</a></div>
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
