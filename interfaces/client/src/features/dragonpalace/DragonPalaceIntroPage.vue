<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goBack = () => {
  router.back()
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="dragonpalace-intro">
    <div class="section title">【龙宫之谜】副本简介</div>

    <div class="section">1.副本在10-24点开放挑战，关卡胜利获得的探索礼包，内含幻兽进化所需的材料。</div>
    <div class="section">2.玩家每天可以免费挑战一次，再次挑战需要花费元宝进行重置次数。</div>
    <div class="section">3.当前关卡挑战成功后，可进入下一关卡挑战</div>

    <div class="section spacer">
      <a class="link" @click="goBack">返回前页</a>
    </div>
    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>
  </div>
</template>

<style scoped>
.dragonpalace-intro {
  background: #FFF8DC;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 13px;
  line-height: 1.6;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 2px 0;
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


