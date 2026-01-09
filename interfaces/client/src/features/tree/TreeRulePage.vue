<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goBack = () => router.back()
const goHome = () => router.push('/')
</script>

<template>
  <div class="tree-rule">
    <div class="section title">古树规则</div>

    <div class="section">每天领取 1 个数字（0-100），一周共领取 7 个数字。</div>
    <div class="section">周日显示本周中奖数字（7个）。</div>
    <div class="section">把“我的数字”和“中奖数字”对比：</div>
    <div class="section indent">命中 5 个及以上：获得 5 星幸运礼包</div>
    <div class="section indent">命中 4 个：获得 4 星幸运礼包</div>
    <div class="section indent">命中 3 个：获得 3 星幸运礼包</div>
    <div class="section indent">命中 2 个：获得 2 星幸运礼包</div>
    <div class="section indent">命中 1 个：获得 1 星幸运礼包</div>

    <div class="section spacer">礼包内容（周日领奖，一周一次）：</div>
    <div class="section indent">1星幸运礼包：1w 铜钱</div>
    <div class="section indent">2星幸运礼包：3w 铜钱</div>
    <div class="section indent">3星幸运礼包：5w 铜钱、重生丹×1</div>
    <div class="section indent">4星幸运礼包：10w 铜钱、重生丹×1</div>
    <div class="section indent">5星幸运礼包：15w 铜钱、重生丹×1</div>

    <div class="section spacer">
      <a class="link" @click="goBack">返回前页</a>
    </div>
    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>
  </div>
</template>

<style scoped>
.tree-rule {
  background: #FFF8DC;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 13px;
  line-height: 1.7;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 2px 0;
}

.title {
  font-weight: bold;
  margin-top: 6px;
}

.indent {
  padding-left: 12px;
}

.spacer {
  margin-top: 10px;
}

.link {
  color: #0033cc;
  cursor: pointer;
  margin-right: 10px;
}
</style>


