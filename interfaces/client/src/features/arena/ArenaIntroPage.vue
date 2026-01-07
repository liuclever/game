<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goArena = () => router.push('/arena')
const goHome = () => router.push('/')
</script>

<template>
  <div class="intro-page">
    <div class="section title">【擂台须知】</div>
    <div class="section">
      擂台是召唤大陆最古老的竞技活动，2星（Lv.20）以上召唤师方能参加。
    </div>
    <div class="section">
      根据召唤师实力，擂台分为：
    </div>
    <div class="section">
      黄阶: Lv.20-29
    </div>
    <div class="section">
      玄阶: Lv.30-39
    </div>
    <div class="section">
      地阶: Lv.40-49
    </div>
    <div class="section">
      天阶: Lv.50-59
    </div>
    <div class="section">
      飞马: Lv.60-69
    </div>
    <div class="section">
      天龙: Lv.70-79
    </div>
    <div class="section">
      战神: Lv.80以上
    </div>

    <div class="section title2">【系统开放】</div>
    <div class="section">08:00 - 24:00</div>

    <div class="section title2">【普通场规则】</div>
    <div class="section gray">1. 每名召唤师每天可挑战10次</div>
    <div class="section gray">2. 每次挑战需要消耗1个捕捉球</div>
    <div class="section gray">3. 挑战成功的玩家成为擂主</div>
    <div class="section gray">4. 挑战消耗的球进入奖池，打赢即可获得奖池全部球</div>
    <div class="section gray">5. 擂主连胜10场后可领取奖池并自动下台</div>

    <div class="section title2">【黄金场规则】</div>
    <div class="section gray">1. 每名召唤师每天可挑战10次</div>
    <div class="section gray">2. 每次挑战需要消耗1个强力捕捉球</div>
    <div class="section gray">3. 挑战成功的玩家成为擂主</div>
    <div class="section gray">4. 挑战消耗的球进入奖池，打赢即可获得奖池全部球</div>
    <div class="section gray">5. 擂主连胜10场后可领取奖池并自动下台</div>

    <div class="section spacer">
      <a class="link" @click="goArena">返回擂台首页</a>
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
  background: #f5f5dc;
  min-height: 100vh;
}
.section { margin: 6px 0; line-height: 1.6; }
.title { font-weight: bold; color: #333; }
.title2 { font-weight: bold; color: #333; margin-top: 12px; }
.gray { color: #666; }
.link { color: #1e90ff; cursor: pointer; text-decoration: none; }
.link:hover { text-decoration: underline; }
.spacer { margin-top: 14px; }
</style>
