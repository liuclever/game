<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goBack = () => router.push('/king')
const goHome = () => router.push('/')
</script>

<template>
  <div class="intro-page">
    <div class="section title">【简介】 <a class="link" @click="goBack">返回</a></div>
    
    <div class="section">1.玩家达到20级可参加挑战赛。</div>
    <div class="section">2.分为预选赛和正赛，每周一0点至23：59为预选赛报名时间。</div>
    <div class="section">3.预选赛于周二0点正式开始，主动挑战匹配对手，若胜利排名上升，若失败排名不变。</div>
    <div class="section">4.每天有15次免费挑战，可使用战令增加挑战次数。</div>
    <div class="section">5.每次挑战后会有60秒冷却时间，冷却后才可继续挑战。</div>
    <div class="section">6.每周四24:00预选赛结束，各区前32名玩家进入正赛。</div>
    <div class="section">7.正赛于每周五12:00开始，决出32强。</div>
    <div class="section">8.每周五13:00决出16强。</div>
    <div class="section">9.每周五14:00决出8强。</div>
    <div class="section">10.每周五15:00决出4强。</div>
    <div class="section">11.每周五16:00决出2强。</div>
    <div class="section">12.每周五17:00决出冠军。</div>
    <div class="section highlight">13.预选赛可获得铜钱奖励，正赛进入32强可获得额外奖励,奖励在。</div>
    <div class="section highlight">14.正赛奖励需要在本周内领取，下周一0点后将无法领取。</div>

    <div class="section spacer">
      <a class="link" @click="goBack">返回挑战赛首页</a>
    </div>
    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>

  </div>
</template>

<style scoped>
.intro-page {
  padding: 10px;
  font-size: 14px;
  background: #FFFFFF;
  min-height: 100vh;
}

.section {
  margin: 8px 0;
  line-height: 1.6;
}

.title {
  font-weight: bold;
  color: #333;
}

.link {
  color: #1e90ff;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.highlight {
  color: #cc0000;
}

.spacer {
  margin-top: 20px;
}

.footer {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #ccc;
}

.gray {
  color: #666;
}

.small {
  font-size: 11px;
}
</style>
